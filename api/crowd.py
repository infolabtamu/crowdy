import cherrypy
from cherrypy import tools
from api.models import Crowd
from utils import get_or_404

@cherrypy.expose
@tools.json_out()
def id(cid):
    """returns all the information about a crowd in a dict"""
    return get_or_404(Crowd,cid).to_d()

@cherrypy.expose
@tools.json_out()
def simple(cid):
    """returns a crowd, after removing information about when users leave
    and join plus when crowds split and merge"""
    return get_or_404(Crowd,cid).simple()
