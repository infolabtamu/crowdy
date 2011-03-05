#!/usr/bin/env python
import traceback
import pdb
import sys

import cherrypy
from cherrypy import tools
import maroon

from etc.settings import settings
import api
import web

if __name__ == '__main__':
    try:
        maroon.Model.database = maroon.MongoDB(
            name=settings.mongo_database,
            host=settings.mongo_host)
        cherrypy.config.update("etc/crowdy.conf")
        cherrypy.tree.mount(api,"/api/1",config="etc/api.conf")
        cherrypy.quickstart(web,"/",config="etc/web.conf")
    except:
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[2])
