#!/usr/bin/python
import sys
sys.path.append('..')

from collections import defaultdict, deque
from itertools import chain
from datetime import datetime, timedelta
import os
import errno


def find_tris(year, month, startday, days):
    hour_edges = deque(maxlen=7)
    start = datetime(int(year), int(month), int(startday))
    hour = timedelta(hours=1)

    #pre-fill the buffer
    for x in xrange(-3,3):
        graph_for_hour(start + x*hour, hour_edges)

    for x in xrange(24*(int(days))):
        read = start+(x+3)*hour
        write = start+x*hour
        graph_for_hour(read, hour_edges)
        if write>=start:
            print "write",
            edges = find_tri_edges(merge_graph(hour_edges))
            save_edges(write,edges)
        print read.timetuple()[:4]


def graph_for_hour(time, hour_edges):
    graph = defaultdict(set)
    path = os.path.join("ats", *[str(n) for n in time.timetuple()[:4]])
    for line in open(path):
        a,b = sorted(int(uid) for uid in line.split()[2:])
        graph[a].add(b)
    hour_edges.append(graph)


def merge_graph(hour_edges):
    #merge 24 dicts
    graph = defaultdict(set)
    for g in hour_edges:
        for k,v in g.iteritems():
            graph[k].update(v)
    return graph


def find_tri_edges(graph):
    "takes a graph and returns the set of edges that make triangles"
    tris = (
        ((me, you), (me, oth), (you, oth))
        for me, mine in graph.iteritems()
        for you in mine
        if you in graph
        for oth in mine&graph[you]
        )
    return set(chain.from_iterable(tris))


def save_edges(time, edges):
    path = _path_time("tri_edge",time)
    mkdir_p(os.path.dirname(path))
    with open(path,'w') as f:
        for e in edges:
            print>>f, e[0], e[1]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno!=errno.EEXIST:
            raise
 

def _path_time(label, time):
    return os.path.join(label, *[str(n) for n in time.timetuple()[:4]])


if __name__ == '__main__':
    find_tris(*sys.argv[1:])
