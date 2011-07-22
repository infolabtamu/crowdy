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
    return _render('crowds.html')


@cherrypy.expose
def search():
    return _render('list.html')


@cherrypy.expose
def about():
    return _render('about.html')


def _chart_html(stamps, crowd):
    counts = defaultdict(int)
    for s in stamps:
        counts[s/3600]+=1
    start = crowd['start']/3600
    end = crowd['end']/3600
    hours = xrange(start,end)
    data = [counts[h] for h in hours]
    print data
    start_dt = dt.utcfromtimestamp(start*3600)

    chart = google_chart_api.Sparkline(data)
    chart.left.min = 0
    chart.left.max = max(data)
    return chart.display.Img(20*math.sqrt(len(data)), 12)

def _user_stamps(hist):
    return chain.from_iterable(
            xrange(seg[0]-3600, seg[1], 3600)
            for seg in hist
            )


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
            tweet_spark = _chart_html(t_stamps, crowd),
            user_spark = _chart_html(u_stamps, crowd),
            crowd = crowd,
            tweet_count = len(t_stamps),
            )
    return dict(crowd=crowd, users=users, tweets=tweets, html=html, index=index)
