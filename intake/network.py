import networkx as nx
import operator
from heapq import nlargest

from etc.settings import settings
from api.models import Crowd, CrowdTweets, User
from intake.module import CrowdFilter


class CrowdNetworkFilter(CrowdFilter): 
    def cfilter(self, crowds):
        for crowd in crowds:
            graph = self.make_graph(crowd._id)
            if not graph:
                print "skipping %s"%crowd._id
                continue
            crowd.clust_coeff = self.clust_coeff(graph)
            self.central_users(crowd, graph)
            self.set_title(crowd)
            yield crowd

    def make_graph(self, cid):
        tweets = CrowdTweets.get_id(cid)
        if not tweets:
            return None
        edges = [ e
            for e in zip(tweets.user_ids, tweets.at_ids)
            if e[0]!=e[1]
        ]
        return nx.Graph(edges)

    def clust_coeff(self, graph):
        return nx.average_clustering(graph)

    def central_users(self, crowd, graph):
        deg = nx.degree_centrality(graph)
        for user in crowd.users:
            user['cent']=deg.get(user['id'],0)
        #pick the 10 users with the greatest centrality
        crowd.central_users = nlargest(10, deg.iterkeys(), key=deg.__getitem__)

    def set_title(self, crowd):
        users = (User.get_id(uid,fields=['sn']) for uid in crowd.central_users)
        names = [u.screen_name for u in users if u][0:2]
        crowd.title = ", ".join(names+["..."])
