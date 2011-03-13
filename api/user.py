import cherrypy
from cherrypy import tools
from api.models import User,Tweet,Edges

@cherrypy.expose
@tools.json_out()
def id(uid):
    return User.get_id(uid).to_d()

@cherrypy.expose
@tools.json_out()
def edges(uid):
    return Edges.get_id(uid).to_d()

@cherrypy.expose
@tools.json_out()
def tweets(uid):
    raise NotImplementedError
