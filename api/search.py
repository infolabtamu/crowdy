#!/usr/bin/env python
import cherrypy
from cherrypy import tools
from time import mktime

def _to_epoch(dt):
    return mktime(dt.timetuple())

@cherrypy.expose
@tools.json_out()
def crowd():
    """returns a list of crowds and their duration"""
    return [
        dict(
            cid=c._id,
            start=_to_epoch(c.start),
            end=_to_epoch(c.end),
            size=len(c.users),
        )
        for c in Crowd.get_all(limit=100)
    ]

