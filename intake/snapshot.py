import sys
sys.path.append('..')

from collections import defaultdict

import maroon

from etc.settings import settings
from api.models import Tweet, User, GraphSnapshot
from datetime import datetime, timedelta


TIME_DELAY = timedelta(seconds=300)


def make_snapshots(year, month, day):
    users = set(u._id for u in User.find(fields=[]))
    time = datetime(int(year), int(month), int(day))
    while(time.day==int(day)):
        graph = make_graph(time, users)
        graph.save()
        time += TIME_DELAY
    print "saved %r"%time


def make_graph(time, users):
    tweets = Tweet.find(Tweet.created_at.range(time, time+TIME_DELAY))
    edges = ((tweet.user_id,at)
        for tweet in tweets
        for at in tweet.mentions
        if tweet.user_id!=at and at in users)

    graph = defaultdict(int)
    for e in edges:
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
