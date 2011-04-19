'''
Created on Apr 11, 2011

@author: kykamath

Unique keys?

'''

import sys
sys.path.append('../')
import lucene, os
from lucene import Document, Field, RAMDirectory, IndexWriter, StandardAnalyzer, Version, IndexSearcher, TopScoreDocCollector, QueryParser, SimpleFSDirectory, Term
from etc.settings import settings
from api.models import Crowd, Tweet
from intake.module import CrowdFilter

hitsPerPage = 100

class CrowdFields:
    id='id'
    text='text'

class CrowdsSearch(CrowdFilter):
    initialized = False
    
    @staticmethod
    def initialize():
        CrowdsSearch.initialized = True
        lucene.initVM()
        CrowdsSearch.index = SimpleFSDirectory(lucene.File(settings.lucene_index_dir))
        CrowdsSearch.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT);
    
    def cfilter(self, crowds):
        def _isDocumentUpdate(crowd):
            try:
                return CrowdsSearch.getCrowds(crowd[CrowdFields.id], CrowdFields.id)
            except:
                return False
        if not CrowdsSearch.initialized:
            CrowdsSearch.initialize()
        mkdir = not os.path.exists(settings.lucene_index_dir)
        writer = IndexWriter(CrowdsSearch.index, CrowdsSearch.analyzer, mkdir, IndexWriter.MaxFieldLength.UNLIMITED)

        for crowd in crowds:
            print "indexing %s"%crowd._id
            tweets = crowd.tweets(limit=None)
            text = "\n".join(t.text for t in tweets)
            doc = Document();
            doc.add(Field(CrowdFields.id, crowd._id, lucene.Field.Store.YES, lucene.Field.Index.NOT_ANALYZED))
            doc.add(Field(CrowdFields.text, text, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED))
            if _isDocumentUpdate(crowd):
                writer.updateDocument(Term(CrowdFields.id, crowd._id), doc)
            else:
                writer.addDocument(doc)
            yield crowd
        writer.close()
    

    @staticmethod
    def getCrowds(query, field = CrowdFields.text): 
        if not CrowdsSearch.initialized: CrowdsSearch.initialize()
        searcher = IndexSearcher(CrowdsSearch.index, True);
        q = QueryParser(Version.LUCENE_CURRENT, field, CrowdsSearch.analyzer).parse(query);
        collector = TopScoreDocCollector.create(hitsPerPage, True);
        searcher.search(q, collector);
        hits = collector.topDocs().scoreDocs
        
        returnData = []
        for scoreDoc in hits:
            doc = searcher.doc(scoreDoc.doc)
            returnData.append({CrowdFields.id: doc.get(CrowdFields.id), CrowdFields.text: doc.get(CrowdFields.text)})
        return returnData
