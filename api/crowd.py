#!/usr/bin/env python
import cherrypy
from cherrypy import tools
from api.models import Crowd

@cherrypy.expose
@tools.json_out()
def full(cid):
    """returns all the information about a crowd in a dict"""
    return Crowd.get_id(cid).to_d()

@cherrypy.expose
@tools.json_out()
def simple(cid):
    """returns a crowd, after removing information about when users leave
    and join plus when crowds split and merge"""
    crowd = Crowd.get_id(cid).to_d()
    del crowd['merge']
    del crowd['split']
    crowd['users'] = [u[0] for u in crowd['users']]
    return crowd
