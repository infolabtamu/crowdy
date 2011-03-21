#!/usr/bin/env python

import sys
sys.path.append("..")
import unittest

import cherrypy
import maroon
from maroon import MockDB

import api
from etc.settings import settings


class TestAPI(unittest.TestCase):
    def setUp(self):
        maroon.Model.database = MockDB("infolabbers",api.models)

    def test_user_id(self):
        jeff = api.user.id('106582358')
        self.failUnlessEqual(jeff['sn'],'JeffAMcGee')
        self.failUnlessRaises(cherrypy.HTTPError, api.user.id, '12')
    
    def test_user_tweets(self):
        #tweets(uid,start_date=None,end_date=None,limit=100):
        jan5 = '1294185600'
        jan16 = '1295136000'
        before = api.user.tweets('106582358',end_date=jan5)
        self.failUnlessEqual(len(before),3)
        after = api.user.tweets('106582358',start_date=jan16)
        self.failUnlessEqual(len(after),4)
        mid = api.user.tweets('106582358',start_date=jan5,end_date=jan16)
        self.failUnlessEqual(len(mid),12)
        lim = api.user.tweets('106582358',limit=5)
        self.failUnlessEqual(len(lim),5)


if __name__ == '__main__':
    unittest.main()