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
        if not CrowdsSearch.initialized:
            CrowdsSearch.initialize()
        mkdir = not os.path.exists(settings.lucene_index_dir)
        self.writer = IndexWriter(CrowdsSearch.index,
            CrowdsSearch.analyzer,
            mkdir,
            IndexWriter.MaxFieldLength.UNLIMITED)
        return self

    def addCrowd(self,id,text):
        doc = Document();
        doc.add(Field(CrowdFields.id, id, Field.Store.YES, Field.Index.NOT_ANALYZED))
        doc.add(Field(CrowdFields.text, text, Field.Store.YES, Field.Index.ANALYZED))
        try:
            CrowdsSearch.getCrowds(id, CrowdFields.id)
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


class CrowdsSearch:
    initialized = False
    
    @staticmethod
    def initialize():
        CrowdsSearch.initialized = True
        lucene.initVM()
        CrowdsSearch.index = SimpleFSDirectory(lucene.File(settings.lucene_index_dir))
        CrowdsSearch.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT);

    @staticmethod
    def getCrowds(query, field = CrowdFields.text): 
        if not CrowdsSearch.initialized:
            CrowdsSearch.initialize()
        searcher = IndexSearcher(CrowdsSearch.index, True);
        q = QueryParser(Version.LUCENE_CURRENT, field, CrowdsSearch.analyzer).parse(query);
        collector = TopScoreDocCollector.create(hitsPerPage, True);
        searcher.search(q, collector);
        hits = collector.topDocs().scoreDocs
        
        return [
            searcher.doc(scoreDoc.doc).get(CrowdFields.id)
            for scoreDoc in hits]
