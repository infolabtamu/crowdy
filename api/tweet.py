import cherrypy
from cherrypy import tools
from api.models import Tweet

@cherrypy.expose
@tools.json_out()
def id(tid):
    return Tweet.get_id(tid).to_d()
