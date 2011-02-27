#!/usr/bin/env python
import cherrypy
from cherrypy import tools
import api

class Root(object):
    pass

if __name__ == '__main__':
    cherrypy.config.update("etc/crowdy.conf")
    cherrypy.tree.mount(api,"/api/1",config="etc/api.conf")
    cherrypy.quickstart(Root(),"/",config="etc/static.conf")
