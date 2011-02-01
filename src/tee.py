#!/usr/bin/env python
import logging
import json

from settings import settings
import module

class Tee(module.UserFilter):
    def __init__(self, path):
        module.UserFilter.__init__(self)
        self.path = path

    def ufilter(self, users):
        f = open(self.path,'w+')
        for user in users:
            user['tee'] = 1+user.get('tee',0)
            print>>f, json.dumps(user)
            yield user
        f.close()

if __name__ == '__main__':
    module.main(Tee)
