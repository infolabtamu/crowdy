import networkx as nx
import operator
from heapq import nlargest

from etc.settings import settings
from api.models import Crowd, Tweet
from intake.module import CrowdFilter


class CrowdNetworkFilter(CrowdFilter): 
    def cfilter(self, crowds):
        for crowd in crowds:
            print "analyzing network for %s"%crowd._id
            tweets = crowd.tweets(limit=0)
            graph = self.make_graph(tweets)
            crowd.clust_coeff = self.clust_coeff(graph)
            self.central_users(crowd, graph)
            yield crowd

    def make_graph(self, tweets):
        edges = [(tweet.user_id,at)
            for tweet in tweets
            for at in tweet.mentions
            if tweet.user_id!=at]
        return nx.Graph(edges)

    def clust_coeff(self, graph):
        return nx.average_clustering(graph)

    def central_users(self, crowd, graph):
        deg = nx.degree_centrality(graph)
        for user in crowd.users:
            user['cent']=deg.get(user['id'],0)
        #pick the 10 users with the greatest centrality
        crowd.central_users = nlargest(10, deg.iterkeys(), key=deg.__getitem__)
