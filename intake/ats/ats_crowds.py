'''
Created on Feb 16, 2011

@author: kykamath
'''
import math, time, os
from pymongo import Connection
from datetime import timedelta
from datetime import datetime

# General settings.
#crawled_data_path = '/mnt/chevron/kykamath/data/twitter/ats/crawler/'
#crowd_path = '/mnt/chevron/kykamath/data/twitter/ats'
data_dir = '/mnt/sid/hou_crowds'
crawled_data_path = '%s/crawler/'%data_dir
crowd_path = data_dir
crowd_type = 'ats'
edge_threshold_weight = 1.3

# DB initialization
mongodb_connection = Connection('localhost', 27017)
crowds_db = mongodb_connection.hou
edges = crowds_db.ats_graph_edges
edges.ensure_index('_id')

crowds_collection = crowds_db.Crowd
crowds_collection.ensure_index('_id')

class CrowdsDB:
    def __init__(self, collection, currentTime): 
        self.collection = collection
        self.currentTime = currentTime
    def save(self, data):
        crowd = self.collection.find_one({'_id': data['_id']})
        if crowd==None: self.__add(data)
        else: self.__update(crowd, data)
    def __add(self, data):
        crowd_object_in_db =  {'_id': data['_id'], 'start': self.currentTime, 'end': None, 'users': [], 
                               'type': crowd_type, 'merge' : [], 'split' : [] }
        for user in data['users']: crowd_object_in_db['users'].append({'id': user,'history': [[self.currentTime, None]]})
        crowd_object_in_db['size'] = len(crowd_object_in_db['users'])
        self.collection.save(crowd_object_in_db)
    def __update(self, crowd, newdata):
        ############# Starting users changes. ####################################
        users = {}
        for user in crowd['users']:
            # Update current user crowd information.
            user_id = user['id']
            users[user_id] = user
            # Update if user has been removed.
            if user_id not in newdata['users']: users[user_id]['history'][-1][1] = self.currentTime
        # Add new and rejoined users.
        for user in newdata['users']:
            if user not in users: 
                # User observed for the first time in crowd.
                users[user] = {'id': user, 'history': [[self.currentTime, None]]}
            else:
                previously_observed_user = users[user]
                if previously_observed_user['history'][-1][1]==None:
                    # User has not left since last observed. So do nothing.
                    pass
                else:
                    # User rejoining the crowd. Add tuple for this new information.
                    previously_observed_user['history'].append([self.currentTime, None])
        # Update user changes in the crowd object.
        crowd['users'] = users.values()
        ############# Ending users changes. ####################################
        
        # Update crowd size (Max. number of users the crowd has ever had).
        current_number_of_users = len(crowd['users'])
        if current_number_of_users>crowd['size']: crowd['size']=current_number_of_users
        
        # Saving updated object in db.
        self.collection.save(crowd)
        
    def updateEndTime(self, crowd_id):
        crowd = self.collection.find_one({'_id': crowd_id})
        crowd['end'] = self.currentTime
        # Saving updated object in db.
        self.collection.save(crowd)
        
    def updateCrowdMerge(self, crowd_id, merged_crowd_id):
        crowd = self.collection.find_one({'_id': crowd_id})
        merge_information = [merged_crowd_id, self.currentTime]
        crowd['merge'].append(merge_information)
        # Saving updated object in db.
        self.collection.save(crowd)
    
    def updateCrowdSplit(self, crowd_id, split_crowd_id):
        crowd = self.collection.find_one({'_id': crowd_id})
        split_information = [split_crowd_id, self.currentTime]
        crowd['split'].append(split_information)
        # Saving updated object in db.
        self.collection.save(crowd)
        
    
class Edges(object):
    @staticmethod
    def add(edge): edges.save(edge)
    @staticmethod
    def update(id, data):
        edge = edges.find_one({'_id': id})
        for k, v in data.iteritems(): edge[k] = v
        edges.save(edge)
    @staticmethod
    def get(id):
        edge = edges.find_one({'_id': id})
        return edge
    @staticmethod
    def delete(id): edges.remove({'_id': id})
    @staticmethod
    def getAllEdges(): return edges.find()
    @staticmethod
    def demo():
        Edges.add('a b', 12, 1)
        for e in Edges.getAllEdges(): print e

class Epoch(object):
    def __init__(self, ep):
        self.ep = ep
        self.dt = datetime.fromtimestamp(self.ep)
    def getGraphId(self):
        tm = time.localtime(self.ep)
        return ':'.join([str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_hour)])
    def getTweetFile(self):
        tm = time.localtime(self.ep)
        return os.sep.join([crawled_data_path, 'time', str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday)])
    def getGraphFile(self, create = False, paramInfo = ''):
        tm = time.localtime(self.ep)
        filePath = os.sep.join([crowd_path, paramInfo, 'graphs', str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_hour)]) 
        if create: self._createDirectory(filePath)
        return filePath
    def getCrowdsFile(self, create = False, paramInfo = ''):
        tm = time.localtime(self.ep)
        filePath = os.sep.join([crowd_path, paramInfo, 'crowds', str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_hour)]) 
        if create: self._createDirectory(filePath)
        return filePath
    def next(self, interval = 1):
        h = timedelta(hours=interval)
        nextTime = self.dt + h
        nextEpochVal = time.mktime(nextTime.timetuple())
        if nextEpochVal == self.ep: nextEpochVal = nextEpochVal + 3600*interval
        return Epoch(nextEpochVal)
    def previous(self, interval = 1):
        h = timedelta(hours=interval)
        nextTime = self.dt - h
        nextEpochVal = time.mktime(nextTime.timetuple())
        if nextEpochVal == self.ep: nextEpochVal = nextEpochVal - 3600*interval
        return Epoch(nextEpochVal)
    def __str__(self): return '%s' % self.dt
    @staticmethod
    def _createDirectory(path):
        dir = path[:path.rfind('/')]
        if not os.path.exists(dir): os.umask(0), os.makedirs('%s'%dir, 0770)

class GraphReader(object):
    def __init__(self, ep, decayCoefficient = 1.0, writeGraph = False):
        self.epoch = ep
        self.decayCoefficient = decayCoefficient
        self.writeGraph = writeGraph
    
    def buildCurrentGraph(self, interval = 1):
        currentTime, graphFile, tweetsFile = self.epoch.ep, None, None
        if self.writeGraph: 
            graphFile = open(self.epoch.getGraphFile(create = True, paramInfo = '%s'%self.decayCoefficient), 'w')
#            tweetsFile = open(self.epoch.getTweetsFile(create = True, paramInfo = '%s'%self.decayCoefficient), 'w')
        tweets = self._updateCurrentEdges(interval)
        def updateEdge(e):
            edge, weight, lastUpdateTime = e['_id'], e['w'], e['lut']
            decayedWeight = self._decayedEdgeWeight(weight, lastUpdateTime, currentTime)
            if decayedWeight == 0: Edges.delete(edge)
            else:
                if e['upr'] != -1:
                    e['lut'] = e['upr']
                    e['upr'] = -1
                e['w'] = decayedWeight
                Edges.add(e)
            if self.writeGraph and decayedWeight > edge_threshold_weight: 
                graphFile.write('%s %s\n'%(edge, decayedWeight))
#                if edge in tweets.keys(): tweetsFile.write('%s %s\n'%(edge, ' '.join(['%s' % id for id in tweets[edge]])))
        map(updateEdge, Edges.getAllEdges())
    
    def _updateCurrentEdges(self, interval):
        low, high, tweetsDict = self.epoch.ep, self.epoch.ep+(interval*3600), {}
        def validateLine(line):
            l = line.strip().split()
            t = int(l[0])
            if len(l) == 4 and t>=low and t<high: return (t, l[1], l[2], l[3])
        for e in filter(lambda e: e != None, 
                      map(validateLine, open(self.epoch.getTweetFile()))):
            edge = ' '.join(sorted([e[2], e[3]]))
            if edge not in tweetsDict.keys(): tweetsDict[edge] = []
            tweetsDict[edge].append(e[1])
            edgeInDB = Edges.get(edge)
            if edgeInDB != None:
                edgeInDB['w'] += 1
                edgeInDB['upr'] = e[0]
                Edges.update(edge, edgeInDB)
            else: Edges.add({'_id':edge, 'w': 1, 'lut': e[0], 'upr': e[0]})
        return tweetsDict
    
    def _decayedEdgeWeight(self, actualWeight, previousEdgeTime, currentEdgeTime):
        returnWeight = 0
        timeDifference = int((currentEdgeTime-previousEdgeTime)/3600)
        if timeDifference > 1: returnWeight = actualWeight - math.log(timeDifference)*self.decayCoefficient
        else: returnWeight = actualWeight
        if returnWeight <= 0: return 0
        else: return int(round(returnWeight))
        
class MCL(object):
    def __init__(self, epoch, I = [], decayCoefficient = 1.0, interval = 1):
        self.epoch = epoch
        self.I = I
        self.decayCoefficient = decayCoefficient
    @staticmethod
    def _graphCluster(data):
        clusters = []
        if data:
            os.environ["PATH"] = os.environ["PATH"]+os.pathsep+'/opt/local/bin'
            mcl_folder = '/tmp/crowdy_dir/'
            if not os.path.exists(mcl_folder): os.mkdir(mcl_folder)
            os.chdir(mcl_folder)
            graph_file = open('graph', 'w')
            dataMap, reverseDataMap = {}, {}
            for i in data: 
                dataMap[i[0]]=i[0].replace(' ', '_').replace('#', ':ilab:')
                dataMap[i[1]]=i[1].replace(' ', '_').replace('#', ':ilab:')
            for k, v in dataMap.iteritems(): reverseDataMap[v] = k
            for i in data: graph_file.write('%s %s %d\n'%(dataMap[i[0]], dataMap[i[1]], i[2]))
            graph_file.close()
            os.system('mcl graph -q x -V all --abc -o graph.out')
            for l in open('graph.out'): clusters.append([reverseDataMap[i] for i in l.strip().split()])
            os.system('rm -rf /tmp/mcl_dir/*')
        return clusters
    def writeClusters(self):
        crowdsFile = open(self.epoch.getCrowdsFile(create = True, paramInfo = '%s'%self.decayCoefficient), 'w')
        data = []
        for line in open(self.epoch.getGraphFile(paramInfo = '%s'%self.decayCoefficient)):
            tempD = line.strip().split()
            data.append((tempD[0], tempD[1], int(tempD[2])))
        clusters, id = {}, 1
        for d in MCL._graphCluster(data): 
            clusters[id] = d
            id+=1
        for i, c in clusters.iteritems(): crowdsFile.write('%s %s :ilab:  :ilab2:  :ilab3: None\n' % (i, ' '.join(sorted(c))))
        crowdsFile.close()

class Crowd(object):
    def __init__(self, crowdId, parentCrowdId, users, clusterTweetIds, userTweetIds):
        self.crowdId = crowdId
        self.parentCrowdId = parentCrowdId
        self.users = users
        self.clusterTweetIds = filter(lambda l: len(str(l)) < 20 , clusterTweetIds)
        self.userTweetIds = filter(lambda l: len(str(l)) < 20 , userTweetIds)
        self.tweets = []
    def __str__(self): return self.crowdId
    
class Crowds(object):
    def __init__(self, epoch, decayCoefficient = 1.0):
        self.epoch = epoch
        self.crowds = None
        self.decayCoefficient = decayCoefficient
    def getCrowds(self):
        if self.crowds==None:
            graphId = self.epoch.getGraphId()
            for line in map(lambda l: l.strip().split(),
                         open(self.epoch.getCrowdsFile(paramInfo = '%s'%self.decayCoefficient))):
                crowd = Crowds.getCrowdFromLine(line, graphId)
                if crowd!=None: self.crowds[crowd.crowdId] = crowd
        return self.crowds
    @staticmethod
    def difference(crowd1, crowd2): return list(set(crowd1.users).intersection(set(crowd2.users)))
    @staticmethod
    def getCrowdFromLine(line, graphId):
        splitIndex, splitIndex2, splitIndex3 = line.index(':ilab:'), line.index(':ilab2:'), line.index(':ilab3:')
        if len(line[1:splitIndex])>=3:
            return Crowd('%s:%s'%(graphId, line[0]), line[splitIndex3+1] ,line[1:splitIndex], 
                         map(lambda id: int(id), line[splitIndex+1:splitIndex2]), 
                         map(lambda id: int(id), line[splitIndex2+1:splitIndex3]))
        else: return None
    def writeCrowds(self):
        crowdsFile = open(self.epoch.getCrowdsFile(create = True, paramInfo = '%s'%self.decayCoefficient), 'w')
        for crowdId in self.crowds: 
            crowd = self.crowds[crowdId]
            id = crowdId.split(':')[-1]
            crowdsFile.write('%s %s :ilab:  :ilab2:  :ilab3: %s\n' % (id, ' '.join(crowd.users), crowd.parentCrowdId))
        crowdsFile.close()
    

class Evolution(object):
    @staticmethod
    def buildCrowdEvolutionGraph(currentEpoch, decayCoefficient = 1.0):
        from operator import itemgetter
        def getParentCrowds(possibleParentCrowds):
            sizeToCrowdMap = {}
            [sizeToCrowdMap.setdefault(possibleParentCrowds[c], []).append(c) for c in possibleParentCrowds.keys()]
            sortedParentCrowds = sorted(sizeToCrowdMap.iteritems(), key=itemgetter(0), reverse=True)
            if sortedParentCrowds: 
                return sortedParentCrowds[0][1]
            else: return ['None']
        # Current crowds are the older crowds and the next crowds are the latest discovered crowds.
        currentCrowdsObject, nextCrowdsObject = Crowds(currentEpoch, decayCoefficient), Crowds(currentEpoch.next(), decayCoefficient)
        crowdsDB = CrowdsDB(crowds_collection, currentEpoch.next().ep)
        currentCrowds, nextCrowds = currentCrowdsObject.getCrowds(), nextCrowdsObject.getCrowds()
        crowdsWithChildren, usersInNextCrowds = [], []
        # Build a map from user to crowd for current crowds
        currentUserToCrowdMap = {}
        for crowd in currentCrowds.itervalues(): [currentUserToCrowdMap.setdefault(user, crowd.crowdId) for user in crowd.users]
        
        for nextCrowd in nextCrowds.itervalues(): 
            users, possibleParentCrowds = [], {}
            users.extend(nextCrowd.users)
            while users:
                currentCrowdId = currentUserToCrowdMap.get(users[0])
                if currentCrowdId != None:
                    currentCrowd = currentCrowds[currentCrowdId]
                    commonUsers = Crowds.difference(currentCrowd, nextCrowd)
                    possibleParentCrowds[currentCrowd.crowdId] = len(commonUsers)
                    [users.remove(u) for u in commonUsers]
                else: users.remove(users[0])
            parentCrowds = getParentCrowds(possibleParentCrowds)
            if len(parentCrowds)==1:
                if parentCrowds[0]=='None':
                    # First time the crowd is observed.
                    crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                    nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                else:
                    # Crowd continues in the current interval with the same parent id.
                    parentCrowd = parentCrowds[0]
                    if parentCrowd not in crowdsWithChildren:
                        # Crowd crowd continued as before.
                        currentCrowd = currentCrowds[parentCrowd]
                        pid=currentCrowd.parentCrowdId
                        if pid=='None': pid=currentCrowd.crowdId
                        crowdsDB.save({'_id': pid, 'users': nextCrowd.users})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = pid
                        crowdsWithChildren.append(currentCrowd.parentCrowdId)
                    else:
                        # The crowd split from the parent.
                        crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                        crowdsDB.updateCrowdSplit(parentCrowd, nextCrowd.crowdId)
            else:
                # Select a parent that has not been already assigned as the parent.
                has_parent, selected_current_crowd_id, selected_parent_crowd_id = False, None, None
                for parentCrowd in parentCrowds:
                    if parentCrowd not in crowdsWithChildren:
                        has_parent, selected_current_crowd_id = True, parentCrowd
                        currentCrowd = currentCrowds[parentCrowd]
                        crowdsDB.save({'_id': currentCrowd.parentCrowdId, 'users': nextCrowd.users})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = currentCrowd.parentCrowdId
                        selected_parent_crowd_id = currentCrowd.parentCrowdId
                        crowdsWithChildren.append(currentCrowd.parentCrowdId)
                        break;
                if not has_parent:
                    # Parent crowds have split into more parts. Create a new crowd for this data.
                    crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                    nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                    for parentCrowd in parentCrowds: crowdsDB.updateCrowdSplit(parentCrowd, nextCrowd.crowdId)
                else:
                    # Remaining parents either merge or split into this.
                    for crowd in parentCrowds:
                        if crowd!=selected_current_crowd_id:
                            crowdUsers = set(currentCrowds[crowd].users)
                            difference = crowdUsers.difference(set(nextCrowd.users))
                            if len(difference)==0:
                                # The crowd has merged into this crowd.
                                crowdsDB.updateCrowdMerge(selected_parent_crowd_id, currentCrowds[crowd].parentCrowdId)
                            else:
                                # The crowd has split into this crowd.
                                crowdsDB.updateCrowdSplit(currentCrowds[crowd].parentCrowdId, selected_parent_crowd_id)
#            print parentCrowds
#            CrowdsDB.saveCrowd({'_id': nextCrowd.crowdId, 'p' : parentCrowds})
#            for parent in parentCrowds: CrowdsDB.saveCrowd({'_id': parent, 'c': [nextCrowd.crowdId]})
#            for user in nextCrowd.users: UTC.saveUserToCrowd({'_id': user, 'b': nextCrowd.crowdId})
#            crowdsWithChildren += parentCrowds
#            usersInNextCrowds += nextCrowd.users
##        
        for currentCrowd in currentCrowds.itervalues():
            if currentCrowd.parentCrowdId not in crowdsWithChildren: crowdsDB.updateEndTime(currentCrowd.parentCrowdId)
            
        nextCrowdsObject.writeCrowds()
        
#                for user in currentCrowd.users: UTC.saveUserToCrowd({'_id': user, 'r': [currentCrowd.crowdId], 'b': ''})
#            for user in filter(lambda u: u not in usersInNextCrowds, currentCrowd.users):
#                UTC.saveUserToCrowd({'_id': user, 'r': [currentCrowd.crowdId], 'b': ''})

    @staticmethod
    def debugBuildCrowdEvolutionGraph(currentCrowdsObject, nextCrowdsObject, currentTime):
        from operator import itemgetter
        def getParentCrowds(possibleParentCrowds):
            sizeToCrowdMap = {}
            [sizeToCrowdMap.setdefault(possibleParentCrowds[c], []).append(c) for c in possibleParentCrowds.keys()]
            sortedParentCrowds = sorted(sizeToCrowdMap.iteritems(), key=itemgetter(0), reverse=True)
            if sortedParentCrowds: 
                return sortedParentCrowds[0][1]
            else: return ['None']
        # Current crowds are the older crowds and the next crowds are the latest discovered crowds.
#        currentCrowdsObject, nextCrowdsObject = Crowds(currentEpoch, decayCoefficient), Crowds(currentEpoch.next(), decayCoefficient)
#        crowdsDB = CrowdsDB(crowds_collection, currentEpoch.next().ep)

        crowdsDB = CrowdsDB(crowds_collection, currentTime)
        currentCrowds, nextCrowds = currentCrowdsObject.getCrowds(), nextCrowdsObject.getCrowds()
        crowdsWithChildren, usersInNextCrowds = [], []
        # Build a map from user to crowd for current crowds
        currentUserToCrowdMap = {}
        for crowd in currentCrowds.itervalues(): [currentUserToCrowdMap.setdefault(user, crowd.crowdId) for user in crowd.users]
        
        for nextCrowd in nextCrowds.itervalues(): 
            users, possibleParentCrowds = [], {}
            users.extend(nextCrowd.users)
            while users:
                currentCrowdId = currentUserToCrowdMap.get(users[0])
                if currentCrowdId != None:
                    currentCrowd = currentCrowds[currentCrowdId]
                    commonUsers = Crowds.difference(currentCrowd, nextCrowd)
                    possibleParentCrowds[currentCrowd.crowdId] = len(commonUsers)
                    [users.remove(u) for u in commonUsers]
                else: users.remove(users[0])
            parentCrowds = getParentCrowds(possibleParentCrowds)
            if len(parentCrowds)==1:
                if parentCrowds[0]=='None':
                    # First time the crowd is observed.
                    crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                    nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                else:
                    # Crowd continues in the current interval with the same parent id.
                    parentCrowd = parentCrowds[0]
                    if parentCrowd not in crowdsWithChildren:
                        # Crowd crowd continued as before.
                        currentCrowd = currentCrowds[parentCrowd]
                        pid=currentCrowd.parentCrowdId
                        if pid=='None': pid=currentCrowd.crowdId
                        crowdsDB.save({'_id': pid, 'users': nextCrowd.users})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = pid
                        crowdsWithChildren.append(currentCrowd.parentCrowdId)
                    else:
                        # The crowd split from the parent.
                        crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                        crowdsDB.updateCrowdSplit(parentCrowd, nextCrowd.crowdId)
            else:
                # Select a parent that has not been already assigned as the parent.
                has_parent, selected_current_crowd_id, selected_parent_crowd_id = False, None, None
                for parentCrowd in parentCrowds:
                    if parentCrowd not in crowdsWithChildren:
                        has_parent, selected_current_crowd_id = True, parentCrowd
                        currentCrowd = currentCrowds[parentCrowd]
                        crowdsDB.save({'_id': currentCrowd.parentCrowdId, 'users': nextCrowd.users})
                        nextCrowds[nextCrowd.crowdId].parentCrowdId = currentCrowd.parentCrowdId
                        selected_parent_crowd_id = currentCrowd.parentCrowdId
                        crowdsWithChildren.append(currentCrowd.parentCrowdId)
                        break;
                if not has_parent:
                    # Parent crowds have split into more parts. Create a new crowd for this data.
                    crowdsDB.save({'_id': nextCrowd.crowdId, 'users': nextCrowd.users, 'type': crowd_type})
                    nextCrowds[nextCrowd.crowdId].parentCrowdId = nextCrowd.crowdId
                    for parentCrowd in parentCrowds: crowdsDB.updateCrowdSplit(parentCrowd, nextCrowd.crowdId)
                else:
                    # Remaining parents either merge or split into this.
                    for crowd in parentCrowds:
                        if crowd!=selected_current_crowd_id:
                            crowdUsers = set(currentCrowds[crowd].users)
                            difference = crowdUsers.difference(set(nextCrowd.users))
                            if len(difference)==0:
                                # The crowd has merged into this crowd.
                                crowdsDB.updateCrowdMerge(selected_parent_crowd_id, currentCrowds[crowd].parentCrowdId)
                            else:
                                # The crowd has split into this crowd.
                                crowdsDB.updateCrowdSplit(currentCrowds[crowd].parentCrowdId, selected_parent_crowd_id)
#            print parentCrowds
#            CrowdsDB.saveCrowd({'_id': nextCrowd.crowdId, 'p' : parentCrowds})
#            for parent in parentCrowds: CrowdsDB.saveCrowd({'_id': parent, 'c': [nextCrowd.crowdId]})
#            for user in nextCrowd.users: UTC.saveUserToCrowd({'_id': user, 'b': nextCrowd.crowdId})
#            crowdsWithChildren += parentCrowds
#            usersInNextCrowds += nextCrowd.users
##        
        for currentCrowd in currentCrowds.itervalues():
            if currentCrowd.parentCrowdId not in crowdsWithChildren: crowdsDB.updateEndTime(currentCrowd.parentCrowdId)
            
        nextCrowdsObject.writeCrowds()
        
#                for user in currentCrowd.users: UTC.saveUserToCrowd({'_id': user, 'r': [currentCrowd.crowdId], 'b': ''})
#            for user in filter(lambda u: u not in usersInNextCrowds, currentCrowd.users):
#                UTC.saveUserToCrowd({'_id': user, 'r': [currentCrowd.crowdId], 'b': ''})

def test_crowdEvolution():
    def getCrowdsFromFile(file, id):
        crowds={}
        for line in open(file):
            line=line.strip().split()
            splitIndex, splitIndex2, splitIndex3 = line.index(':ilab:'), line.index(':ilab2:'), line.index(':ilab3:')
            crowd = Crowd('%s:%s'%(id, line[0]), line[splitIndex3+1] ,line[1:splitIndex], 
                             map(lambda id: int(id), line[splitIndex+1:splitIndex2]), 
                             map(lambda id: int(id), line[splitIndex2+1:splitIndex3]))
            crowds[crowd.crowdId]=crowd
            crowdObject = Crowds(None)
            crowdObject.crowds = crowds
        return crowdObject
    currentCrowdsObject, nextCrowdsObject = getCrowdsFromFile('crowds/crowds1', '1'), getCrowdsFromFile('crowds/crowds2', '2')
    Evolution.debugBuildCrowdEvolutionGraph(currentCrowdsObject, nextCrowdsObject, 1)
        
if __name__ == '__main__':
#    MCL.demo()
#    Evolution.demo()    
    test_crowdEvolution()