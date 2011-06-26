import sys
sys.path.append('.')

import os
from collections import defaultdict
from datetime import datetime, timedelta
from bisect import bisect_right

from bson.code import Code
import maroon

from api.models import Crowd, CrowdTime, CrowdTweets
from etc.settings import settings


def mr_crowds(db):
    map = Code("""
        function() {
            var seconds = 1000;
            var t = 3600*Math.floor(this.start/3600/seconds);
            var end = this.end/seconds|| 1288224000;
            while(t<end) {
                emit( new Date(t*1000), {crowds:[this._id]} );
                t+=3600;
            }
        }
    """)
    #GRR. Mongodb demands that the values be objects, not arrays.
    reduce = Code("""
        function (key, values) {
            var res = {crowds:[]};
            values.forEach(function(val) {
                res.crowds.push.apply(res.crowds, val.crowds);
            });
            return res;
        }
    """)
    db.Crowd.map_reduce(map, reduce, "CrowdTime")


def _path_time(label, time):
    return os.path.join(label, *[str(n) for n in time.timetuple()[:4]])


def crowd_tweets(year, month, startday, days=1):
    time = start = datetime(int(year), int(month), int(startday))
    end = start+timedelta(days=int(days))
    keys = ['dts','tids','uids','aids']
    while time <end:
        at_path = _path_time("tri_ats",time)
        tweets = [
            [int(s) for s in line.split()]
            for line in open(at_path)
        ]
        crowd_time = CrowdTime.get_id(time)
        if crowd_time:
            print "crowds for %r"%time
            crowds = Crowd.find(Crowd._id.is_in(crowd_time.value['crowds']))
        else:
            print "no crowds at %r"%time
            crowds = []
        krishna_time = time+timedelta(hours=1)
        for crowd in crowds:
            #figure out who is in the crowd this hour
            members = set(
                user['id']
                for user in crowd.users
                if user['history'][0][0]<=krishna_time<=user['history'][-1][-1]
            )
            if not members:
                print "an empty crowd?"
                import pdb; pdb.set_trace()
            #find tweets between crowd members
            d = defaultdict(list)
            for tweet in tweets:
                if tweet[2] in members and tweet[3] in members:
                    for k,v in zip(keys,tweet):
                        d[k].append(v)
            #save the new crowd
            if d:
                d['dts'] = [datetime.utcfromtimestamp(t) for t in d['dts']]
                CrowdTweets.coll().find_and_modify(
                    {'_id':crowd._id},
                    {'$pushAll':d},
                    upsert=True,
                    )
        time = time+timedelta(hours=1)


if __name__ == '__main__':
    db = maroon.Model.database = maroon.MongoDB(
        name="hou",
        host=settings.mongo_host)
    cmd = sys.argv[1]
    if cmd=='hourly':
        mr_crowds(db)
    elif cmd=='index':
        crowd_tweets(*sys.argv[2:])
    else:
        print "unknown command: %s"%cmdP
