'''
Created on Apr 13, 2011

@author: kykamath
'''
import sys, os
sys.path.append('../../')
import unittest
from etc.settings import settings
from intake.search import CrowdSearcher, CrowdIndexer

testIndexFolder = '/tmp/search_test'

class TwitterSearchTest(unittest.TestCase):
    def setUp(self):
        settings.lucene_index_dir = testIndexFolder
        os.system('rm -rf %s'%settings.lucene_index_dir)
        
    def test_generalCrowdSearch(self):
        searcher = CrowdSearcher()
        with CrowdIndexer() as index:
            index.addCrowd('1',u'Lucene in Action')
            index.addCrowd('2',u'Lucene for Dummies')
            index.addCrowd('3',u'Managing Gigabytes')
            index.addCrowd('4',u'The Art of Computer Science')
            index.addCrowd('5',u'The Art of Computer Science and Engineering')
        self.assertEqual(['1','2'], searcher.getCrowds('lucene'))
        self.assertEqual(['4','5'], searcher.getCrowds('science'))
    
    def test_updateCrowdSearch(self):
        searcher = CrowdSearcher()
        docBeforeUpdate = {'id': '1', 'text': 'Lucene in Action'}
        docAfterUpdate = {'text': 'Lucene for Dummies', 'id': '1'}
        
        with CrowdIndexer() as index:
            index.addCrowd(**docBeforeUpdate)
        self.assertEqual(['1'], searcher.getCrowds('action'))
            
        with CrowdIndexer() as index:
            index.addCrowd(**docAfterUpdate)
        self.assertEqual([], searcher.getCrowds('action'))
        self.assertEqual(['1'], searcher.getCrowds('dummies'))
        
if __name__ == '__main__': 
    unittest.main()
