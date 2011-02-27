#!/usr/bin/env python
import cherrypy
from cherrypy import tools

@cherrypy.expose
@tools.json_out()
def crowd():
    """returns all the information about a crowd in a dict"""
    raise NotImplementedError
    #return Crowd.database.find()[0-10]

