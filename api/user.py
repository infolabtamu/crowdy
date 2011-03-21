import cherrypy
from cherrypy import tools
from api.models import User,Tweet,Edges
from utils import parse_date, get_or_404

@cherrypy.expose
@tools.json_out()
def id(uid):
    return get_or_404(User,int(uid)).to_d()

@cherrypy.expose
@tools.json_out()
def edges(uid):
    return get_or_404(Edges,int(uid)).to_d()

@cherrypy.expose
@tools.json_out()
def tweets(uid,start_date=None,end_date=None,limit=100):
    start = parse_date(start_date)
    end = parse_date(end_date)
    limit = int(limit) if limit else None
    tweets = Tweet.find(
        (Tweet.user_id==int(uid)) &
        (Tweet.created_at.range(start,end)),
        limit=limit,
        sort=Tweet._id)
    return [t.to_d() for t in tweets]
