import cherrypy
from cherrypy import tools
from time import mktime
from api.models import Crowd

def _to_epoch(dt):
    if dt!=None: return mktime(dt.timetuple())

@cherrypy.expose
@tools.json_out()
def crowd(**kwargs):
    """returns a list of crowds and their duration"""
    return [
        dict(
            cid=c._id,
            start=_to_epoch(c.start),
            end=_to_epoch(c.end),
            size=len(c.users),
        )
        for c in Crowd.get_all(limit=100)
    ]

@cherrypy.expose
@tools.json_out()
def crowd_by_size(comparator, size):
    """returns crowds for a given size"""
    valid_comparators = ['eq', 'gte', 'lt']
    if comparator not in valid_comparators: return {'error': 'Invalid comparator. Use one of %s'%(', '.join(valid_comparators)) }
    
    crowdsToReturn = []
    if comparator=='eq': crowdsToReturn = [c for c in Crowd.find(Crowd.size==int(size))]
    elif comparator=='gte': crowdsToReturn = [c for c in Crowd.find(Crowd.size>=int(size))]
    else: crowdsToReturn = [c for c in Crowd.find(Crowd.size<int(size))]
    
    return [
        dict(
            cid=c._id,
            start=_to_epoch(c.start),
            end=_to_epoch(c.end),
            size=c.size,
        )
        for c in crowdsToReturn
    ]
