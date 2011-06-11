#!/usr/bin/python
import sys
sys.path.append('..')

from collections import defaultdict, deque
from itertools import chain
from datetime import datetime, timedelta
import os
import errno

class TriangleFinder():
    def __init__(self, window_size):
        self.hour_edges = deque(maxlen=2*window_size+1)
        self.graph = {}
        self.edges = set()
        self.window = window_size

    def find_tris(self, year, month, startday, days):
        start = datetime(int(year), int(month), int(startday))
        hour = timedelta(hours=1)

        #pre-fill the buffer
        for x in xrange(-self.window,self.window):
            self.graph_for_hour(start + x*hour)

        for x in xrange(24*(int(days))):
            read = start+(x+self.window)*hour
            write = start+x*hour
            self.graph_for_hour(read)
            if write>=start:
                self.merge_graph()
                self.find_tri_edges()
                self.save_edges(write)
            print write.timetuple()[:4]

    def graph_for_hour(self, time, ):
        graph = defaultdict(set)
        path = _path_time("ats",time)
        for line in open(path):
            a,b = sorted(int(uid) for uid in line.split()[2:])
            graph[a].add(b)
        self.hour_edges.append(graph)

    def merge_graph(self, ):
        #merge the dicts
        self.graph = defaultdict(set)
        for g in self.hour_edges:
            for k,v in g.iteritems():
                self.graph[k].update(v)

    def find_tri_edges(self, ):
        "takes a graph and returns the set of edges that make triangles"
        tris = (
            ((me, you), (me, oth), (you, oth))
            for me, mine in self.graph.iteritems()
            for you in mine
            if you in self.graph
            for oth in mine&self.graph[you]
            )
        self.edges = set(chain.from_iterable(tris))

    def save_edges(self, time):
        path = _path_time("tri_edge",time)
        mkdir_p(os.path.dirname(path))
        with open(path,'w') as f:
            for e in self.edges:
                print>>f, e[0], e[1]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno!=errno.EEXIST:
            raise
 

def _path_time(label, time):
    return os.path.join(label, *[str(n) for n in time.timetuple()[:4]])


def tri_filter(year, month, startday, days):
    time = start = datetime(int(year), int(month), int(startday))
    end = start+timedelta(days=int(days))

    while time <end:
        #read edges
        edge_path = _path_time("tri_edge",time)
        tri_edges = set(
            tuple(int(id) for id in line.split())
            for line in open(edge_path))

        #filter
        at_path = _path_time("ats",time)
        save_path = _path_time("tri_ats",time)
        mkdir_p(os.path.dirname(save_path))
        with open(save_path,'w') as f:
            for line in open(at_path):
                a,b = sorted(int(uid) for uid in line.split()[2:])
                if (a,b) in tri_edges:
                    print >>f, line,
         
        time = time+timedelta(hours=1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd=='find':
        TriangleFinder(window_size=3).find_tris(*sys.argv[2:])
    elif cmd=='filter':
        tri_filter(*sys.argv[2:])
    else:
        print "unknown command: %s"%cmd
