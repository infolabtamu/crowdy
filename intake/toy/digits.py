#!/usr/bin/env python
import logging

from etc.settings import settings
from .. import module

class Digits(module.Grouper):
    def __init__(self, digits=2):
        module.Grouper.__init__(self)
        self.digits = int(digits)

    def group(self, users):
        groups = [
                dict(label="digits_"+str(x).zfill(self.digits), uids=[])
                for x in xrange(10**self.digits)
                ]
        for user in users:
            index = int(user['id'])%(10**self.digits)
            groups[index]['uids'].append(user['id'])
        return groups

if __name__ == '__main__':
    module.main(Digits)
