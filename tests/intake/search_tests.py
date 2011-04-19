'''
Created on Apr 13, 2011

@author: kykamath
'''
import sys, os
sys.path.append('../../')
import unittest
from etc.settings import settings
from intake.search import CrowdsSearch, CrowdIndexer

testIndexFolder = '/tmp/search_test'

class TwitterSearchTest(unittest.TestCase):
    def setUp(self):
        settings.lucene_index_dir = testIndexFolder
        os.system('rm -rf %s'%settings.lucene_index_dir)
        
    def test_generalCrowdSearch(self):
        with CrowdIndexer() as index:
            index.addCrowd('1',u'Lucene in Action')
            index.addCrowd('2',u'Lucene for Dummies')
            index.addCrowd('3',u'Managing Gigabytes')
            index.addCrowd('4',u'The Art of Computer Science')
            index.addCrowd('5',u'The Art of Computer Science and Engineering')
        self.assertEqual([{'text': u'Lucene in Action', 'id': u'1'}, {'text': u'Lucene for Dummies', 'id': u'2'}], CrowdsSearch.getCrowds('lucene'))
        self.assertEqual([{'text': u'The Art of Computer Science', 'id': u'4'}, {'text': u'The Art of Computer Science and Engineering', 'id': u'5'}], CrowdsSearch.getCrowds('science'))
    
    def test_updateCrowdSearch(self):
        docBeforeUpdate = {'id': '1', 'text': 'Lucene in Action'}
        docAfterUpdate = {'text': 'Lucene for Dummies', 'id': '1'}
        
        with CrowdIndexer() as index:
            index.addCrowd(**docBeforeUpdate)
            self.assertEqual([docBeforeUpdate], CrowdsSearch.getCrowds('action'))
            
            index.addCrowd(**docAfterUpdate)
            self.assertNotEqual([docAfterUpdate], CrowdsSearch.getCrowds('action'))
            self.assertEqual([docAfterUpdate], CrowdsSearch.getCrowds('dummies'))
    
    def tearDown(self):
        os.system('rm -rf %s'%testIndexFolder)
        
if __name__ == '__main__': 
    unittest.main()
