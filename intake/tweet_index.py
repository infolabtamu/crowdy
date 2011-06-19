import sys
sys.path.append('.')

import os
from collections import defaultdict
from datetime import datetime, timedelta

from bson.code import Code
import maroon

from api.models import Crowd
from etc.settings import settings

def mr_crowds(db):
    map = Code("""
        function() {
            var seconds = 1.0/1000;
            var t = 3600*Math.floor(this.start/3600*seconds);
            var end = this.end*seconds|| 1288224000;
            while(t<end) {
                emit( t, {crowds:[this._id]} );
                t+=3600;
            }
        }
    """)
    #GRR. Mongodb demands that the values be objects, not arrays.
    reduce = Code("""
        function (key, values) {
            var res = {crowds:[]};
            values.forEach(function(val) {
                res.crowds.push.apply(val.crowds);
            });
            return res;
        }
    """)
    db.Crowd.map_reduce(map, reduce, "crowdtime")

def mr_users(db):
    #FIXME: Buggy!
    map = Code("""
        function() {
            var crowd_end = this.end || 1308449555;
            this.users.forEach(function(user) {
                user.history.forEach(function(slice) {
                    var t = 3600*Math.floor(slice[0]/3600);
                    var end = slice[1] || crowd_end;
                    while(t<end) {
                        emit(t,{u:user.id,c:this._id});
                        t+=3600;
                    }
                });
            });
        }
    """)
    reduce = Code("""
        function (key, values) {
            var res = {};
            values.forEach(function(row) {
                if (!res.hasOwnProperty(row.c)) {
                    res[row.c] = new Array();
                }
                res[row.c].push(row.u);
            });
            return res;
        }
    """)
    db.Crowd.map_reduce(map, reduce, "crowdcount")

if __name__ == '__main__':
    db = maroon.Model.database = maroon.MongoDB(
        name=sys.argv[1],
        host=settings.mongo_host)
    mr_crowds(db)
