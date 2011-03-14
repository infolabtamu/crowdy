#These are modules that we want to include in the api.
import crowd
import search
import user
import tweet

import cherrypy
from cherrypy import tools

@cherrypy.expose
@tools.json_out()
def status():
    return dict(status='ok')
