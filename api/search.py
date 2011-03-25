import cherrypy
from cherrypy import tools
from api.models import Crowd
from utils import parse_bool, parse_date, range_from_params

@cherrypy.expose
@tools.json_out()
def crowd(q="", limit='100', simple='t', **kwargs):
    """returns a list of crowds - by default it returns 100 crowds unsorted in
    the simple format - without information about merges and joins
    q is the query - this is not implemented yet
    search/crowd
        returns 100 crowds
    search/crowd?min_start=1294185600&limit=none
        returns all the crowds that staterd after Jan 5, 2011
    search/crowd?max_size=5&min_end=1295136000&q=love&limit=none
        returns all the crowds where a tweet contains the word love, there
        are at least five twitter users in the crowd, and the crowd ends
        after Jan 16, 2011.
    search/crowd?simple=false&limit=10
        returns 10 crowds in the full format
    """
    crowds = Crowd.find(
            range_from_params(Crowd, 'start', parse_date, kwargs) &
            range_from_params(Crowd, 'end', parse_date, kwargs) &
            range_from_params(Crowd, 'size', int, kwargs),
            limit=int(limit) if limit.lower()!="none" else None)
    transform = Crowd.simple if parse_bool(simple) else Crowd.to_d
    return [ transform(c) for c in crowds]
