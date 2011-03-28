from time import mktime
from datetime import datetime
import cherrypy

def to_epoch(dt):
    if dt!=None: return mktime(dt.timetuple())

def parse_bool(bstr):
    return bstr.lower() in ['t','true','1']

def parse_date(dstr):
    if not dstr: return None
    return datetime.utcfromtimestamp(float(dstr))

def range_from_params(cls, key, filter, kwargs):
    start = kwargs.get('min_'+key)
    end = kwargs.get('max_'+key)
    return getattr(cls,key).range(
            None if start is None else filter(start),
            None if end is None else filter(end))

def get_or_404(cls,id):
    obj = cls.get_id(id)
    if obj is None:
        raise cherrypy.HTTPError(404,
            'There is no %s with id "%s"!'%(cls.__name__,str(id)))
    return obj
