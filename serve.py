#!/usr/bin/env python
import traceback
import pdb
import sys

import cherrypy
from cherrypy import tools
from cherrypy.process import plugins, servers
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

    try:
        maroon.Model.database = maroon.MongoDB(
            name=settings.mongo_database,
            host=settings.mongo_host)

        if settings.production:
            cherrypy.config.update("etc/crowdy_prod.conf")
            cherrypy.tree.mount(api,"/api/1",config="etc/api.conf")
            cherrypy.tree.mount(web, "/", config="etc/web.conf")

            # taken from the cherryd script
            engine = cherrypy.engine
            if hasattr(engine, "signal_handler"):
                engine.signal_handler.subscribe()
            if hasattr(engine, "console_control_handler"):
                engine.console_control_handler.subscribe()
            cherrypy.server.unsubscribe()
            addr = cherrypy.server.bind_addr
            f = servers.FlupFCGIServer(application=cherrypy.tree,
                                       bindAddress=addr)
            s = servers.ServerAdapter(engine, httpserver=f, bind_addr=addr)
            s.subscribe()

            engine.start()
            engine.block()
        else:
            cherrypy.config.update("etc/crowdy.conf")
            cherrypy.tree.mount(api,"/api/1",config="etc/api.conf")
            cherrypy.quickstart(web,"/",config="etc/web.conf")
    except:
        traceback.print_exc()

