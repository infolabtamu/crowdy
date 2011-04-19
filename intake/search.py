'''
Created on Apr 11, 2011

@author: kykamath

Unique keys?

'''

import sys
sys.path.append('../')
import lucene, os
from lucene import Document, Field, IndexWriter, StandardAnalyzer, Version, IndexSearcher, TopScoreDocCollector, QueryParser, SimpleFSDirectory, Term, JavaError
from etc.settings import settings
from api.models import Crowd, Tweet
from intake.module import CrowdFilter

hitsPerPage = 100

class CrowdFields:
    id='id'
    text='text'


class CrowdIndexer():
    def __enter__(self):
        self.searcher = CrowdSearcher()
        mkdir = not os.path.exists(settings.lucene_index_dir)
        self.writer = IndexWriter(self.searcher.index,
            self.searcher.analyzer,
            mkdir,
            IndexWriter.MaxFieldLength.UNLIMITED)
        return self

    def addCrowd(self,id,text):
        doc = Document();
        doc.add(Field(CrowdFields.id, id, Field.Store.YES, Field.Index.NOT_ANALYZED))
        doc.add(Field(CrowdFields.text, text, Field.Store.YES, Field.Index.ANALYZED))
        try:
            self.searcher.getCrowds(id, CrowdFields.id)
            self.writer.updateDocument(Term(CrowdFields.id, id), doc)
        except JavaError:
            self.writer.addDocument(doc)

    def __exit__(self, type, value, traecback):
        self.writer.close()


class CrowdIndexFilter(CrowdFilter): 
    def cfilter(self, crowds):
        with CrowdIndexer() as index:
            for crowd in crowds:
                print "indexing %s"%crowd._id
                tweets = crowd.tweets(limit=None)
                text = "\n".join(t.text for t in tweets)
                index.addCrowd(crowd._id,text)
                yield crowd


class CrowdSearcher:
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.__shared_state:
            self.jccvm = lucene.initVM()
            self.index = SimpleFSDirectory(lucene.File(settings.lucene_index_dir))
            self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

    def getCrowds(self, query, field = CrowdFields.text): 
        searcher = IndexSearcher(self.index, True)
        q = QueryParser(Version.LUCENE_CURRENT, field, self.analyzer).parse(query)
        collector = TopScoreDocCollector.create(hitsPerPage, True)
        searcher.search(q, collector)
        hits = collector.topDocs().scoreDocs
        
        return [
            searcher.doc(scoreDoc.doc).get(CrowdFields.id)
            for scoreDoc in hits]
