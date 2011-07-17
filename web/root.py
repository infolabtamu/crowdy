#!/usr/bin/env python
import cherrypy
from cherrypy import tools
import api.crowd
import math
from itertools import chain
import datetime
from datetime import datetime as dt
from collections import defaultdict

from graphy.backends import google_chart_api
from graphy import common

from jinja2 import Environment, FileSystemLoader
#FIXME: I don't like that this is a global variable - Jeff
_env = Environment(loader=FileSystemLoader('web/templates'))


def _render(path, **kwargs):
    return _env.get_template(path).render(**kwargs)


@cherrypy.expose
def index():
    return _render('index.html')


@cherrypy.expose
def list():
    return _render('list.html')


@cherrypy.expose
def snapshot():
    return _render('snapshot.html')


@cherrypy.expose
def crowds():
    return _render('crowds.html')


def _chart_html(stamps):
    counts = defaultdict(int)
    for s in stamps:
        counts[s/3600]+=1
    start, end = min(counts.keys()),max(counts.keys())
    hours = xrange(start,end+1)
    data = [counts[h] for h in hours]
    start_dt = dt.utcfromtimestamp(start*3600)

    chart = google_chart_api.Sparkline(data)
    chart.left.min = 0
    chart.left.max = max(data)
    return chart.display.Img(20*math.sqrt(len(data)), 12)

def _user_stamps(hist):
    print hist[0][0], hist[-1][-1]
    return xrange(hist[0][0], hist[-1][-1]-3600, 3600)


@tools.json_out()
@cherrypy.expose
def crowd(cid):
    crowd = api.crowd.id(cid)
    users = api.crowd.users(cid)
    tweets = api.crowd.tweets(cid)
    index = api.crowd.tweet_index(cid)
    del index['tids']
    t_stamps = [int(t) for t in index['dts']]
    u_stamps = chain.from_iterable(
                _user_stamps(u['history'])
                for u in crowd['users'])
    html = _render(
            'crowd.html',
            tweet_spark = _chart_html(t_stamps),
            user_spark = _chart_html(u_stamps),
            crowd = crowd,
            tweet_count = len(t_stamps),
            )
    return dict(crowd=crowd, users=users, tweets=tweets, html=html, index=index)
