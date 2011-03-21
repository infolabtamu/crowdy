from time import mktime
from datetime import datetime
import cherrypy

def to_epoch(dt):
    if dt!=None: return mktime(dt.timetuple())

def parse_date(dstr):
    if not dstr: return None
    return datetime.utcfromtimestamp(float(dstr))

def get_or_404(cls,id):
    obj = cls.get_id(int(id))
    if obj is None:
        raise cherrypy.HTTPError(404,
            'There is no %s with id "%d"!'%(cls.__name__,int(id)))
    return obj
