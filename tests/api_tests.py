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

if __name__ == '__main__':
    unittest.main()
