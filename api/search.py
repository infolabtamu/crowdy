import cherrypy
from cherrypy import tools
from api.models import Crowd
from utils import parse_bool, parse_date, range_from_params

@cherrypy.expose
@tools.json_out()
def crowd(q="", limit='100', sort=None, simple='t', **kwargs):
    """Returns a list of crowds.
    
    Here are some useful parameters:

    simple
        if true, remove details about merges and joins from the crowd
    q
        text to search for (not implemented)
    sort
        how to sort the results (not implemented)
    limit
        maximum number of crowds to return
    {min,max}_start
        when the crowd was formed
    {min,max}_end
        when the crowd ended
    {min,max}_size
        the number of users involved in the crowd

    Here are some example calls:

    /api/1/search/crowd
        returns 100 crowds

    /api/1/search/crowd?min_start=1294185600&limit=none
        returns all the crowds that staterd after Jan 5, 2011

    /api/1/search/crowd?max_size=5&min_end=1295136000&q=love&limit=none
        returns all the crowds where a tweet contains the word love, there
        are at least five twitter users in the crowd, and the crowd ends
        after Jan 16, 2011.

    /api/1/search/crowd?simple=false&limit=10
        returns 10 crowds in the full format
    """
    crowds = Crowd.find(
            range_from_params(Crowd, 'start', parse_date, kwargs) &
            range_from_params(Crowd, 'end', parse_date, kwargs) &
            range_from_params(Crowd, 'size', int, kwargs),
            limit=int(limit) if limit.lower()!="none" else None)
    transform = Crowd.simple if parse_bool(simple) else Crowd.to_d
    return [ transform(c) for c in crowds]
