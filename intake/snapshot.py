import sys
sys.path.append('..')

from collections import defaultdict

import maroon
import os

from api.models import Tweet, User, GraphSnapshot
from etc.settings import settings
from datetime import datetime, timedelta


TIME_DELAY = timedelta(seconds=300)


def make_snapshots(year, month, day):
    users = set(u._id for u in User.find(fields=[]))
    import pdb; pdb.set_trace()
    for hour in xrange(24):
        #load tri_edges
        path = os.path.join("tri_edges", year, month, day, str(hour))
        tri_edges = set(
            tuple(int(id) for id in line.split())
            for line in open(path))
        #process this hour
        time = datetime(int(year), int(month), int(day), hour)
        while time.hour==int(hour):
            graph = make_graph(time, users, tri_edges)
            graph.save()
            time += TIME_DELAY
    print "saved %s/%s/%s"%(year,month,day)


def make_graph(time, users, tri_edges):
    tweets = Tweet.find(Tweet.created_at.range(time, time+TIME_DELAY))
    edges = ((tweet.user_id,at)
        for tweet in tweets
        for at in tweet.mentions
        if tweet.user_id!=at and at in users)

    graph = defaultdict(int)
    for e in edges:
        if tuple(sorted(e)) in tri_edges:
            graph[e]+=1

    return GraphSnapshot(
        _id = time,
        from_ids = (k[0] for k in graph.iterkeys()),
        to_ids = (k[1] for k in graph.iterkeys()),
        weights = graph.itervalues(),
        )

if __name__ == '__main__':
    maroon.Model.database = maroon.MongoDB(
        name=sys.argv[1],
        host=settings.mongo_host)
    make_snapshots(*sys.argv[2:])
