'''
Created on Jul 20, 2011

@author: kykamath
'''
import cherrypy, sys, os

class HelloWorld:
    def index(self):
        return "Hello world! ilab"
    index.exposed = True
    
if "--fastcgi" in sys.argv:
#    app = cherrypy.tree.mount(HelloWorld())
#    # CherryPy autoreload must be disabled for the flup server to work
#    cherrypy.config.update('hello.conf')
#    cherrypy.config.update({'engine.autoreload_on':False})
#    cherrypy.config.update({
#            "tools.sessions.on": True,
#            "tools.sessions.timeout": 5,
#            "log.screen": False,
#            "log.access_file": "/tmp/cherry_access.log",
#            "log.error_file": "/tmp/cherry_error.log",
#    })
#    from flup.server.fcgi import WSGIServer
#    cherrypy.config.update({'engine.autoreload_on':False})
#    WSGIServer(app).run()

    app = cherrypy.tree.mount(HelloWorld())
    cherrypy.config.update(os.path.dirname(os.path.abspath(__file__))+'/hello.conf')
    # CherryPy autoreload must be disabled for the flup server to work
    cherrypy.config.update({'engine.autoreload_on':False})
    from flup.server.fcgi import WSGIServer
    WSGIServer(app, bindAddress=('0.0.0.0', 8000)).run()
else:
    cherrypy.quickstart(HelloWorld(), config="hello.conf")


#!/usr/bin/python
#import cherrypy
#from cherrypy.process import servers
#
#class HelloWorld:
#    """Sample request handler class."""
#    def index(self):
#        return "Hello world!"
#    index.exposed = True
#
#cherrypy.tree.mount(HelloWorld())
## CherryPy autoreload must be disabled for the flup server to work
#cherrypy.config.update({'engine.autoreload_on':False})


#addr = ('0.0.0.0', 8000)
#f = servers.FlupFCGIServer(application=HelloWorld(), bindAddress=addr)
#s = servers.ServerAdapter(cherrypy.engine, httpserver=f, bind_addr=addr)
#s.subscribe()


#cherrypy.quickstart(HelloWorld(), config="hello.conf")