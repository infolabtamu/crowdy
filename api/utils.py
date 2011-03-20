from time import mktime


def to_epoch(dt):
    if dt!=None: return mktime(dt.timetuple())

def parse_date(dstr):
    if not dstr: return None
    if dstr[0]=="[":
