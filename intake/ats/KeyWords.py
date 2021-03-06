'''
Created on Jul 4, 2011

@author: kykamath
'''

from pymongo import Connection
from nlp import getPhrases, getWordsFromRawEnglishMessage
from itertools import groupby
from operator import itemgetter

class KeyWords:
    mongodb_connection = Connection('sarge', 27017)
    tweets = mongodb_connection.hou.Tweet
    crowds = mongodb_connection.hou.Crowd
    crowdTweets = mongodb_connection.hou.CrowdTweets
    
    @staticmethod
    def getTweetsForCrowdId(crowdId):
        tids = KeyWords.crowdTweets.find_one({'_id': crowdId}, fields=['tids'])['tids']
        tweets = []
        for id in tids:
            tweet = KeyWords.tweets.find_one({'_id': id}, fields=['tx'])
            if tweet!=None: tweets.append(tweet['tx'])
        return tweets
    @staticmethod
    def getKeyWordsFromDocuments(documents):
        phrases = []
        for d in documents: phrases+=getPhrases(getWordsFromRawEnglishMessage(d), 2, 2)
        phrasesDistribution = sorted([(k, len(list(g))) for k,g in groupby(sorted(phrases))], key=itemgetter(1), reverse=True)
        hashtags, nonhashtags = [], []
        for p,_ in phrasesDistribution:
            if p.startswith('#'): hashtags.append(p)
            else: nonhashtags.append(p)
        numberOfNonHashtags = 3
        if len(hashtags[:3])<3: numberOfNonHashtags=6-len(hashtags[:3])
        return nonhashtags[:numberOfNonHashtags]+hashtags[:3]
    @staticmethod
    def addKeyWordsForCrowds():
        i = 1
        for crowd in KeyWords.crowds.find():
            crowd['kw'] = KeyWords.getKeyWordsFromDocuments(KeyWords.getTweetsForCrowdId(crowd['_id']))
            print i, crowd['_id'], crowd['kw']
            KeyWords.crowds.save(crowd)
            i+=1

if __name__ == '__main__':
    KeyWords.addKeyWordsForCrowds()