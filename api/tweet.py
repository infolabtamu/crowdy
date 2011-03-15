import cherrypy
from cherrypy import tools
from api.models import Tweet

@cherrypy.expose
@tools.json_out()
def id(uid):
    return Tweet.get_id(uid).to_d()
