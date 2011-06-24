'''
Created on Feb 21, 2011

@author: kykamath
'''
import sys
from pymongo.connection import Connection, database
sys.path.append('../../intake/ats')
import unittest
from operator import itemgetter
from ats_crowds import Epoch, GraphReader, MCL, Evolution, CrowdsDB
from datetime import datetime as dt

#TEST_STARTING_EPOCH = 1280639087
#TEST_ENDING_EPOCH = 1288846743
#TEST_CURRENT_EPOCH = 1283317200

TEST_STARTING_EPOCH = 1304208000
#TEST_STARTING_EPOCH = 1291348799
TEST_ENDING_EPOCH = 1306886399
TEST_CURRENT_EPOCH = 1283317200
TEST_TYPE = 'ats'

mongodb_connection = Connection('localhost', 27017)
crowds_db = mongodb_connection.crowds_test
crowds_collection = crowds_db.ats_crowds
crowds_collection.ensure_index('_id')


class DemoCrowdGeneration:
    @staticmethod
    def test_graphReader():
        currentEpoch = Epoch(TEST_STARTING_EPOCH)
        last_epoch = TEST_ENDING_EPOCH
        while currentEpoch.ep < last_epoch:
            print 'Creating graph for: ', str(currentEpoch)
            gr = GraphReader(currentEpoch, decayCoefficient = 1.0, writeGraph = True)
            gr.buildCurrentGraph()
            currentEpoch = currentEpoch.next()
    @staticmethod    
    def test_mcl():
        currentEpoch = Epoch(TEST_STARTING_EPOCH)
        last_epoch = TEST_ENDING_EPOCH
        while currentEpoch.ep < last_epoch:
            print 'Generating crowds for: ', str(currentEpoch)
            mcl = MCL(currentEpoch, I = [1.4])
            mcl.writeClusters()
            currentEpoch = currentEpoch.next()
    @staticmethod    
    def test_evolution():
        currentEpoch = Epoch(TEST_STARTING_EPOCH)
        last_epoch = TEST_ENDING_EPOCH
        i = 0
        while currentEpoch.ep < last_epoch:
            print 'Generating crowd evolution for: ', str(currentEpoch)
            Evolution.buildCrowdEvolutionGraph(currentEpoch)
            currentEpoch = currentEpoch.next()
    @staticmethod
    def test_postPorcessing():
        mongodb_connection = Connection('localhost', 27017)
        crowds_db = mongodb_connection.fake
        crowds_collection = crowds_db.Crowd
        for crowd in crowds_collection.find():
            for k in ['start','end']:
                crowd[k] = dt.utcfromtimestamp(crowd[k]) if crowd[k] else dt(2011,6,1)
            end = crowd['end']
            for user in crowd['users']:
                user['id'] = int(user['id'])
                for h in user['history']:
                    for x in xrange(2):
                        h[x] = dt.utcfromtimestamp(h[x]) if h[x] else end
            crowds_collection.save(crowd)
    @staticmethod
    def demo():
#       DemoCrowdGeneration.test_graphReader()
#       DemoCrowdGeneration.test_mcl()
 #       DemoCrowdGeneration.test_evolution()        
        DemoCrowdGeneration.test_postPorcessing()
    

class CrowdsDBTests(unittest.TestCase):
    def setUp(self):
        crowds_db.drop_collection(crowds_collection)
        self.crowdsDB = CrowdsDB(crowds_collection, TEST_CURRENT_EPOCH)
    
    def test_newCrowdAdd(self):
        data_to_save = {'_id': 1, 'users': ['user1', 'user2'], 'type': 'ats'}
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                       'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ], 
                       'type': 'ats',
                        'merge' : [],
                        'split' : []
                        }
        self.crowdsDB.save(data_to_save)
        actual_object_in_db = crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)
    
    def test_crowdUpdateUserJoin(self):
        # Create existing DB state.
        existing_data = {'_id': 1, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(existing_data)
        
        # Performing test
        user_join_time = 1283400000
        user_added_data = {'_id': 1, 'users': ['user1', 'user2', 'user3'], 'type': 'ats'}
        self.crowdsDB = CrowdsDB(crowds_collection, user_join_time)
        self.crowdsDB.save(user_added_data)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                       'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,None]]},
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                 {'id':'user3','history': [[user_join_time,None]]}
                                ], 
                       'type': 'ats',
                        'merge' : [],
                        'split' : []
                        }
        actual_object_in_db =crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)


    def test_crowdUpdateUserDrop(self):
        # Create existing DB state.
        new_crowd = {'_id': 1, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(new_crowd) 
        
        # User leaves crowd
        user_leave_time = 1283400000
        user_leaves_crowd = {'_id': 1, 'users': ['user2'], 'type': 'ats'}
        self.crowdsDB = CrowdsDB(crowds_collection, user_leave_time)
        self.crowdsDB.save(user_leaves_crowd)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                        'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,user_leave_time]]},
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ], 
                        'type': 'ats',
                        'merge' : [],
                        'split' : []
                        }
        actual_object_in_db = crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)

    def test_crowdUpdateUserRejoin(self):
        # Create existing DB state.
        new_crowd = {'_id': 1, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(new_crowd) 
        
        # User leaves crowd
        user_leave_time = 1283400000
        user_leaves_crowd = {'_id': 1, 'users': ['user2'], 'type': 'ats'}
        self.crowdsDB = CrowdsDB(crowds_collection, user_leave_time)
        self.crowdsDB.save(user_leaves_crowd)
        
        # User rejoines crowd
        user_rejoin_time = 1283700000
        user_rejoins_crowd = {'_id': 1, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB = CrowdsDB(crowds_collection, user_rejoin_time)
        self.crowdsDB.save(user_rejoins_crowd)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                        'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH, user_leave_time], [user_rejoin_time, None]]},
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ],
                       'type': 'ats',
                        'merge' : [],
                        'split' : []
                        }
        actual_object_in_db = crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)

    def test_crowdMerge(self):
        crowd_id, merged_crowd_id = 1, 2
        merge_time = 1283700000
        new_crowd_data = {'_id': crowd_id, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(new_crowd_data)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                       'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ], 
                       'type': 'ats',
                        'merge' : [[merged_crowd_id, merge_time]],
                        'split' : []
                        }
        
        self.crowdsDB = CrowdsDB(crowds_collection, merge_time)
        self.crowdsDB.updateCrowdMerge(crowd_id, merged_crowd_id) 
        actual_object_in_db=crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)

    def test_crowdSplit(self):
        crowd_id, split_crowd_id = 1, 2
        split_time = 1283700000
        new_crowd_data = {'_id': crowd_id, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(new_crowd_data)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': None,
                       'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ], 
                       'type': 'ats',
                        'merge' : [],
                        'split' : [[split_crowd_id, split_time]]
                        }
        
        self.crowdsDB = CrowdsDB(crowds_collection, split_time)
        self.crowdsDB.updateCrowdSplit(crowd_id, split_crowd_id) 
        actual_object_in_db=crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)
        
    def test_crowdUpdateEndTime(self):
        crowd_id = 1
        end_time = 1283700000
        new_crowd_data = {'_id': crowd_id, 'users': ['user1', 'user2'], 'type': 'ats'}
        self.crowdsDB.save(new_crowd_data)
        
        expected_object_in_db = {'_id': 1, 'start': TEST_CURRENT_EPOCH, 'end': end_time,
                       'users': [
                                 {'id':'user1','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                 {'id':'user2','history': [[TEST_CURRENT_EPOCH,None]]}, 
                                ], 
                       'type': 'ats',
                        'merge' : [],
                        'split' : []
                        }
        
        self.crowdsDB = CrowdsDB(crowds_collection, end_time)
        self.crowdsDB.updateEndTime(crowd_id) 
        actual_object_in_db=crowds_collection.find_one({'_id': 1})
        actual_object_in_db['users'] = sorted([user.items() for user in actual_object_in_db['users']], key=itemgetter(0))
        expected_object_in_db['users'] = sorted([user.items() for user in expected_object_in_db['users']], key=itemgetter(0))
        self.assertEqual(expected_object_in_db, actual_object_in_db)
        
if __name__ == '__main__':
#    unittest.main()
    DemoCrowdGeneration.demo()
