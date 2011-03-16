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
def tweets(uid,start=None,end=None):
    #FIXME: write parse_time
    start = parse_time(start)
    end = parse_time(end)
    tweets = Tweet.find(
        (Tweet.user_id==int(uid)) &
        (Tweet.created_at.range(start,end)))
    return [t.to_d() for t in tweets]
