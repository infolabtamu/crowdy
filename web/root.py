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
