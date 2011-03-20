from time import mktime
from datetime import datetime

def to_epoch(dt):
    if dt!=None: return mktime(dt.timetuple())

def parse_date(dstr):
    if not dstr: return None
    return datetime.utcfromtimestamp(float(dstr))
