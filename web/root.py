#!/usr/bin/env python
import cherrypy
from cherrypy import tools
import api.crowd
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
def advanced_search():
    return _render('advanced_search.html')


CHART_WIDTH = 335
CHART_HEIGHT = 150


def _label_axis(axis,hours,delta,format):
    positions = [h for h in hours if h%delta==0]
    axis.min = hours[0]
    axis.max = hours[-1]
    axis.label_positions = positions
    axis.labels = [
            dt.utcfromtimestamp(p*3600).strftime(format)
            for p in positions]


def _chart_html(stamps):
    counts = defaultdict(int)
    for s in stamps:
        counts[s/3600]+=1
    start, end = min(counts.keys()),max(counts.keys())
    hours = range(start-1,end+2)
    data = [counts[h] for h in hours]
    start_dt = dt.utcfromtimestamp(start*3600)
    
    chart = google_chart_api.LineChart(data)
    if len(hours)>=48:
        _label_axis(chart.bottom,hours,24,"%m/%e")
    else:
        if len(hours)>=9:
            _label_axis(chart.bottom,hours,6,"%H:00")
        else:
            _label_axis(chart.bottom,hours,1,"%H:00")
        day_axis = chart.AddAxis(common.AxisPosition.BOTTOM, common.Axis())
        _label_axis(day_axis,hours,24,"%m/%e")

    chart.left.min = 0
    chart.left.max = max(data)
    chart.left.labels = [chart.left.max*i/4 for i in range(1,5)]
    chart.left.label_positions = chart.left.labels
    
    return chart.display.Img(CHART_WIDTH, CHART_HEIGHT)


@cherrypy.expose
def crowd(cid):
    tweets = api.crowd.tweets(cid)
    stamps = [int(t['ca']) for t in tweets]

    return _render('crowd.html',
            cid=cid,
            time_chart=_chart_html(stamps))
