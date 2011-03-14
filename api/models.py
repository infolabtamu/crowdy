import datetime
try:
    import simplejson as json
except:
    import json
import logging

import maroon
from maroon import *


class TwitterIdProperty(IntProperty):
    pass


class TwitterDateTimeProperty(DateTimeProperty):
    def  __init__(self, name, **kwargs):
        format="%a %b %d %H:%M:%S +0000 %Y"
        DateTimeProperty.__init__(self, name, format, **kwargs)


class User(Model):
    _id = TwitterIdProperty('_id')
   
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


class Tweet(Model):
    _id = TwitterIdProperty('_id')
    mentions = SlugListProperty('ats') #based on entities

    #properties from twitter
    coordinates = Property('coord')
    created_at = TwitterDateTimeProperty('ca')
    favorited = BoolProperty('fav')
    geo = Property('geo')
    in_reply_to_status_id = TwitterIdProperty('rtt')
    in_reply_to_user_id = TwitterIdProperty('rtu')
    place = Property('plc')
    text = TextProperty('tx')
    user_id = TwitterIdProperty('uid')


class Edges(Model):
    # I only store the first 5000 friends and followers
    _id = TwitterIdProperty('_id')
    friends = ListProperty('frs',int)
    followers = ListProperty('fols',int)


class Crowd(Model):
    _id = TextProperty('_id')
    start = DateTimeProperty('start')
    end = DateTimeProperty('end')
    type = EnumProperty('type', ['ats','geo','txt'])
    users = ListProperty('users')
    merge = ListProperty('merge')
    split = ListProperty('split')
    size = IntProperty('size')
