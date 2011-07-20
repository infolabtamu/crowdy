#!/usr/bin/env python
import traceback
import pdb, os
import sys

import cherrypy
from cherrypy import tools
import maroon

from etc.settings import settings
import api
import web

if __name__ == '__main__':
    try:
        import api.search
        import intake.search
        #if lucene is not installed, search won't work
        searcher = intake.search.CrowdSearcher()
        cherrypy.engine.subscribe('start_thread',
            lambda x: searcher.jccvm.attachCurrentThread())
    except ImportError:
        print "WARNING: ignoring lucene"

#    try:
    maroon.Model.database = maroon.MongoDB(
        name=settings.mongo_database,
        host=settings.mongo_host)
    # Code added for fastcgi
    if "--fastcgi" in sys.argv:
#            app = cherrypy.tree.mount(api)
        cherrypy.tree.mount(api,os.path.dirname(os.path.abspath(__file__))+"/api/1",config=os.path.dirname(os.path.abspath(__file__))+"/etc/api.conf")
        cherrypy.tree.mount(web,os.path.dirname(os.path.abspath(__file__))+"/web",config=os.path.dirname(os.path.abspath(__file__))+"/etc/web.conf")
        
        # CherryPy autoreload must be disabled for the flup server to work
        cherrypy.config.update({'engine.autoreload_on':False})
        cherrypy.config.update({
                "tools.sessions.on": True,
                "tools.sessions.timeout": 5,
                "log.screen": False,
                "log.access_file": "/tmp/cherry_access.log",
                "log.error_file": "/tmp/cherry_error.log",
        })
        from flup.server.fcgi import WSGIServer
        cherrypy.config.update({'engine.autoreload_on':False})
        WSGIServer(web).run()
    else:
        cherrypy.config.update("etc/crowdy.conf")
        cherrypy.tree.mount(api,"/api/1",config="etc/api.conf")
        cherrypy.quickstart(web,"/",config="etc/web.conf")
#    except:
#        traceback.print_exc()
#        pdb.post_mortem(sys.exc_info()[2])
