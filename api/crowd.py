import cherrypy
from cherrypy import tools
from api.models import Crowd,User,Tweet,Edges, CrowdSnapshot, CrowdTweets
from utils import get_or_404, parse_bool, parse_date

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

@cherrypy.expose
@tools.json_out()
def users(cid):
    "returns all the users in a crowd"
    crowd = get_or_404(Crowd,cid)
    uids = [u['id'] for u in crowd.users]
    users = User.find(User._id.is_in(uids))
    return [u.to_d() for u in users]


@cherrypy.expose
@tools.json_out()
def tweets(cid, page=0):
    "returns all the tweets in a crowd"
    index = get_or_404(CrowdTweets,cid)
    tweets = index.tweets(int(page))
    return [t.to_d() for t in tweets]


@cherrypy.expose
@tools.json_out()
def tweet_index(cid):
    "returns the edges that make up the crowd"
    index = get_or_404(CrowdTweets,cid)
    return index.to_d()


@cherrypy.expose
@tools.json_out()
def star(cid,starred='t'):
    "star or unstar a crowd"
    #FIXME: this should verify that it was a POST
    crowd = get_or_404(Crowd,cid)
    starred = parse_bool(starred)
    if starred!=crowd.star:
        crowd.star = starred
        crowd.save()
    return crowd.simple()

@cherrypy.expose
@tools.json_out()
def sizes(date):
    sizes = get_or_404(CrowdSizes, parse_date(date))
    return sizes.to_d()

#This should go somewhere else. Tweet?
@cherrypy.expose
@tools.json_out()
def snapshot(date):
    graph = get_or_404(CrowdSnapshot, parse_date(date))
    return graph.to_d()
