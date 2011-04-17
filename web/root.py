#!/usr/bin/env python
import cherrypy
from cherrypy import tools

from jinja2 import Environment, FileSystemLoader
#FIXME: I don't like that this is a global variable - Jeff
_env = Environment(loader=FileSystemLoader('web/templates'))

def _render(path, **kwargs):
    return _env.get_template(path).render(**kwargs)

@cherrypy.expose
def index():
    return _render('index.html')

@cherrypy.expose
def list():
    return _render('list.html')

#@cherrypy.expose
#def search():
#    return _render('search.html')

@cherrypy.expose
def advanced_search():
    return _render('advanced_search.html')

@cherrypy.expose
def crowd(cid):
    return _render('crowd.html',cid=cid)

