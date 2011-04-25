import os,sys
import logging
import json

from etc.settings import settings
from api.models import *


class Module(object):
    def run(self):
        raise NotImplementedError


class Crawler(Module):
    def crawl(self):
        """ loads users using the twitter api, streaming, or another source
            yields user dictionaries containing tweets
        """
        raise NotImplementedError

    def run(self):
        for user in self.crawl():
            print json.dumps(user)


class Filter(Module):
    def __init__(self):
        self.users = {}

    def fetch_user(self, uid, crawl=False):
        """ loads the user from the database
            if crawl is True and the user is not in the database, it will
            ask a crawler to lookup the user and return it
        """
        if uid in self.users:
            return self.users[uid]
        if crawl:
            raise NotImplementedError
        return None

    def _users(self):
        # I went to some trouble here to store the users as they come in, and
        # still call ufilter as soon as it gets the first user.  This code
        # would be simpler if it just slurped in everything and passed a list
        # to ufilter.
        for l in sys.stdin:
            u = json.loads(l.strip())
            self.users[u['id']] = u
            yield u


class UserFilter(Filter):
    def ufilter(self, users):
        """ filters a list of users and their tweets
            users is an iterable that is a list of twitter user dictionaries
            yields user dictionaries containing tweets
        """
        raise NotImplementedError

    def run(self):
        for user in self.ufilter(self._users()):
            print json.dumps(user)


class TweetFilter(Filter): # do we want this?
    def tfilter(self, tweets):
        """ filters a list of tweets
            tweets is an iterable that is a list of twitter tweet dictionaries
            yields tweet dictionaries
        """
        raise NotImplementedError

    def run(self):
        pass


class CrowdFilter(Filter):
    def cfilter(self, crowds):
        """ filters a list of crowds
            crowds is an iterable that is a list of crowd dictionaries
            yields crowd objects
        """
        raise NotImplementedError

    def run(self):
        crowds = Crowd.get_all()
        for crowd in self.cfilter(crowds):
            pass


class Grouper(Filter):
    def group(self, users):
        """ breaks a list of users into groups
            users is an iterable that is a list of twitter user dictionaries
            yields group dictionaries
        """
        raise NotImplementedError

    def run(self):
        for group in self.group(self._users()):
            print json.dumps(group)


def main(ModuleType,*args):
    """This method should be called when a Module is executed as the
    __main__ module."""
    #Set up logging
    filepath = os.path.join(
            settings.log_dir,
            ModuleType.__name__.lower()
        )
    logging.basicConfig(filename=filepath,level=logging.INFO)
    #create and run the module
    mod = ModuleType(*args)
    mod.run()
