import cherrypy
from cherrypy import tools
from api.models import User,Tweet,Edges
from utils import parse_date, get_or_404

@cherrypy.expose
@tools.json_out()
def id(uid):
    "returns a user profile for the given id, or raises 404"
    return get_or_404(User,int(uid)).to_d()

@cherrypy.expose
@tools.json_out()
def edges(uid):
    """returns the first 5000 friends and follewers for the given user id, or
    raises 404"""
    return get_or_404(Edges,int(uid)).to_d()

@cherrypy.expose
@tools.json_out()
def tweets(uid,min_date=None,max_date=None,limit=100):
    "returns all the tweets for a user between min_date and max_date"
    start = parse_date(min_date)
    end = parse_date(max_date)
    limit = int(limit) if limit else None
    tweets = Tweet.find(
        (Tweet.user_id==int(uid)) &
        (Tweet.created_at.range(start,end)),
        limit=limit,
        sort=Tweet._id)
    return [t.to_d() for t in tweets]
