import cherrypy
from cherrypy import tools
from api.models import Tweet
from utils import get_or_404

@cherrypy.expose
@tools.json_out()
def id(tid):
    "returns a tweet for the given id, or raises 404"
    return get_or_404(Tweet,int(tid)).to_d()
