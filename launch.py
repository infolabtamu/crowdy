#!/usr/bin/env python

if __name__ != '__main__':
    print """
This is a tool for testing and administrative tasks.  It is designed to
be %run in ipython or from the command line.  If you import it from another
module, you're doing something wrong.  
"""

import logging
import sys
import pdb

import maroon

from intake.module import main
from etc.settings import settings

if len(sys.argv)==2:
    print "runs a module on a region"
    print "./launch.py [region] [class name]"
elif len(sys.argv)>2:
    try:
        maroon.Model.database = maroon.MongoDB(
            name=sys.argv[1],
            host=settings.mongo_host)
        mod_name,cls_name = sys.argv[2].rsplit('.',1)
        mod = __import__(mod_name,fromlist=[cls_name])
        cls = getattr(mod,cls_name)
        obj = cls(*sys.argv[3:])
        obj.run()
    except:
        logging.exception("command failed")
        pdb.post_mortem()
else:
    #get ready for an interactive session
    from api.models import Crowd,Tweet,User,Edges
    logging.basicConfig(level=logging.INFO)
    maroon.Model.database = maroon.MongoDB(
        name = settings.mongo_database,
        host=settings.mongo_host)
