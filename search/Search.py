'''
Created on Apr 11, 2011

@author: kykamath
'''
import lucene, os
from lucene import Document, Field, RAMDirectory, IndexWriter, StandardAnalyzer, Version, IndexSearcher, TopScoreDocCollector, QueryParser, SimpleFSDirectory

indexDirectory = '/tmp/twitter_search'
hitsPerPage = 10;

lucene.initVM()
index = SimpleFSDirectory(lucene.File(indexDirectory))
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT);

class TwitterSearch:
    @staticmethod
    def addTweet(tweet): TwitterWriter().addDoc(tweet)
    @staticmethod
    def getTweets(query): return TwitterSearcher().search(query)

class TwitterWriter:
    def __init__(self): 
        if os.path.exists(indexDirectory): self.writer = IndexWriter(index, analyzer, False, IndexWriter.MaxFieldLength.UNLIMITED)
        else: self.writer = IndexWriter(index, analyzer, True, IndexWriter.MaxFieldLength.UNLIMITED)
    def addDoc(self, tweet):
        doc = Document();
        tweetId, tweetContent = tweet['id'], unicode(tweet['text'], 'iso-8859-1')
        doc.add(Field("id", tweetId, lucene.Field.Store.YES, lucene.Field.Index.NOT_ANALYZED))
        doc.add(Field("text", tweetContent, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED))
        self.writer.addDocument(doc);
        self.writer.close()

class TwitterSearcher:
    def __init__(self): self.searcher = IndexSearcher(index, True);
    def _convertJArrrayToTweetList(self, scoreDocs):
        returnData = []
        for scoreDoc in scoreDocs:
            doc = self.searcher.doc(scoreDoc.doc)
            returnData.append({'id': doc.get('id'), 'text': doc.get('text')})
        return returnData
    def search(self, query):
        q = QueryParser(Version.LUCENE_CURRENT, 'text', analyzer).parse(query);
        collector = TopScoreDocCollector.create(hitsPerPage, True);
        self.searcher.search(q, collector);
        hits = collector.topDocs().scoreDocs
        return self._convertJArrrayToTweetList(hits)

class Demo():
    @staticmethod
    def twitterWriter():
        os.system('rm -rf %s'%indexDirectory)
        TwitterSearch.addTweet({'id': '1', 'text': 'Lucene in Action'})
        TwitterSearch.addTweet({'id': '2', 'text': 'Lucene for Dummies'})
        TwitterSearch.addTweet({'id': '3', 'text': 'Managing Gigabytes'})
        TwitterSearch.addTweet({'id': '4', 'text': 'The Art of Computer Science'})
        TwitterSearch.addTweet({'id': '5', 'text': 'The Art of Computer Science and Engineering'})
    @staticmethod
    def twitterSearcher():
        print TwitterSearch.getTweets('lucene')
        print TwitterSearch.getTweets('science')
if __name__ == '__main__':
    Demo.twitterWriter()
    Demo.twitterSearcher()