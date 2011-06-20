import datetime
from datetime import timedelta
try:
    import simplejson as json
except:
    import json
import logging

import maroon
from maroon import *


class TwitterModel(Model):
    def __init__(self, from_dict=None, **kwargs):
        Model.__init__(self, from_dict, **kwargs)
        if self._id is None and from_dict and 'id' in from_dict:
            self._id = from_dict['id']

    def to_d(self, dateformat="epoch", **kwargs):
        #change the default dateformat to epoch
        return Model.to_d(self, dateformat=dateformat, **kwargs)

class TwitterIdProperty(IntProperty):
    pass


class TwitterDateTimeProperty(DateTimeProperty):
    def  __init__(self, name, **kwargs):
        format="%a %b %d %H:%M:%S +0000 %Y"
        DateTimeProperty.__init__(self, name, format, **kwargs)


class User(TwitterModel):
    _id = TwitterIdProperty('_id')
    ignored = [
        'contributors_enabled', 'follow_request_sent', 'following',
        'profile_background_color', 'profile_background_image_url',
        'profile_background_tile', 'profile_link_color',
        'profile_sidebar_border_color', 'profile_sidebar_fill_color',
        'profile_text_color', 'profile_use_background_image',
        'show_all_inline_media', 'time_zone', 'status', 'notifications',
        'id', 'id_str', 'is_translator',
        # ncd and lcd were added to work around differences between datetimes in
        # localcrawl and crowdy. - Jeff
        'ncd','lcd',
    ]
    
    #properties from twitter
    verified = BoolProperty("ver")
    created_at = TwitterDateTimeProperty('ca')
    description = TextProperty('descr')
    favourites_count = IntProperty('favc')
    followers_count = IntProperty('folc')
    friends_count = IntProperty('frdc')
    geo_enabled = BoolProperty('geo')
    lang = TextProperty('lang')
    listed_count = IntProperty('lsc')
    location = TextProperty('loc')
    name = TextProperty('name')
    profile_image_url = TextProperty('img')
    protected = BoolProperty('prot')
    screen_name = TextProperty('sn')
    statuses_count = IntProperty('stc')
    url = TextProperty('url')
    utc_offset = IntProperty('utco')


class Tweet(TwitterModel):
    _id = TwitterIdProperty('_id')
    mentions = ListProperty('ats',int) #based on entities

    ignored = [
        'contributors', 'entities', 'in_reply_to_screen_name', 'source',
        'truncated', 'user', 'id', 'id_str', 'retweeted', 'retweeted_status',
        'retweeted_count', 'favorited', 'geo', 'user_id_str'
        ]

    #properties from twitter
    coordinates = Property('coord')
    created_at = TwitterDateTimeProperty('ca')
    in_reply_to_status_id = TwitterIdProperty('rtt')
    in_reply_to_user_id = TwitterIdProperty('rtu')
    place = Property('plc')
    text = TextProperty('tx')
    user_id = TwitterIdProperty('uid')

    def __init__(self, from_dict=None, **kwargs):
        TwitterModel.__init__(self, from_dict, **kwargs)
        if self.user_id is None and 'user' in from_dict:
            self.user_id = from_dict['user']['id']
        if self.mentions is None and 'entities' in from_dict:
            ats = from_dict['entities']['user_mentions']
            self.mentions = [at['id'] for at in ats ]

class Edges(TwitterModel):
    # I only store the first 5000 friends and followers
    _id = TwitterIdProperty('_id')
    friends = ListProperty('frs',int)
    followers = ListProperty('fols',int)


class Crowd(TwitterModel):
    _id = TextProperty('_id')
    start = DateTimeProperty('start')
    end = DateTimeProperty('end')
    type = EnumProperty('type', ['ats','geo','txt'])
    users = ListProperty('users')
    merge = ListProperty('merge')
    split = ListProperty('split')
    size = IntProperty('size')
    clust_coeff = FloatProperty('clco')
    central_users = ListProperty('cenus')
    star = BoolProperty('star',default=False)
    title = TextProperty('title')

    def simple(self):
        crowd = self.to_d()
        del crowd['merge']
        del crowd['split']
        crowd['users'] = [u['id'] for u in crowd['users']]
        return crowd

    def tweets(self,limit=1000):
        "returns all of the tweets involved in the crowd"
        if self.type!='ats':
            raise NotImplementedError
        uids = [u['id'] for u in self.users]
        return Tweet.find(
            Tweet.user_id.is_in(uids)&
            Tweet.mentions.is_in(uids)&
            Tweet.created_at.range(self.start, self.end),
            limit=limit,
            sort=Tweet._id)


class GraphSnapshot(TwitterModel):
    _id = DateTimeProperty('_id')
    from_ids = ListProperty('fids',int)
    to_ids = ListProperty('tids',int)
    weights = ListProperty('ws')


class CrowdTime(TwitterModel):
    _id = DateTimeProperty('_id')
    value = DictProperty('value')


class CrowdTweets(TwitterModel):
    _id = TextProperty('_id')
    user_ids = ListProperty('uids',int)
    at_ids = ListProperty('aids',int)
    tweet_ids = ListProperty('tids',int)
    times = ListProperty('dts')
