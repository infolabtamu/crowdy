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

hitsPerPage = 100

class CrowdFields:
    id='id'
    text='text'

class CrowdsSearch:
    initialized = False
    
    @staticmethod
    def initialize():
        CrowdsSearch.initialized = True
        lucene.initVM()
        CrowdsSearch.index = SimpleFSDirectory(lucene.File(settings.lucene_index_dir))
        CrowdsSearch.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT);
    
    @staticmethod
    def addCrowd(crowd): 
        def _isDocumentUpdate(crowd):
            try:
                return CrowdsSearch.getCrowds(crowd[CrowdFields.id], CrowdFields.id)
            except: return False
        if not CrowdsSearch.initialized: CrowdsSearch.initialize()
        if os.path.exists(settings.lucene_index_dir): writer = IndexWriter(CrowdsSearch.index, CrowdsSearch.analyzer, False, IndexWriter.MaxFieldLength.UNLIMITED)
        else: writer = IndexWriter(CrowdsSearch.index, CrowdsSearch.analyzer, True, IndexWriter.MaxFieldLength.UNLIMITED)
        doc = Document();
        crowdId, crowdContent = crowd[CrowdFields.id], unicode(crowd[CrowdFields.text], 'iso-8859-1')
        doc.add(Field(CrowdFields.id, crowdId, lucene.Field.Store.YES, lucene.Field.Index.NOT_ANALYZED))
        doc.add(Field(CrowdFields.text, crowdContent, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED))
        if _isDocumentUpdate(crowd): writer.updateDocument(Term(CrowdFields.id, crowd[CrowdFields.id]), doc)
        else: writer.addDocument(doc)
        writer.close()
    
    @staticmethod
    def getCrowds(query, field = CrowdFields.text): 
        def _convertJArrrayToCrowdList(scoreDocs):
            returnData = []
            for scoreDoc in scoreDocs:
                doc = searcher.doc(scoreDoc.doc)
                returnData.append({CrowdFields.id: doc.get(CrowdFields.id), CrowdFields.text: doc.get(CrowdFields.text)})
            return returnData
        
        if not CrowdsSearch.initialized: CrowdsSearch.initialize()
        searcher = IndexSearcher(CrowdsSearch.index, True);
        q = QueryParser(Version.LUCENE_CURRENT, field, CrowdsSearch.analyzer).parse(query);
        collector = TopScoreDocCollector.create(hitsPerPage, True);
        searcher.search(q, collector);
        hits = collector.topDocs().scoreDocs
        return _convertJArrrayToCrowdList(hits)
