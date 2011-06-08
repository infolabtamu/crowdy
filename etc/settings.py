import pdb
class SettingsBunch(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

settings = SettingsBunch(
    mongo_host = 'sarge.csdl.tamu.edu',
    mongo_database = 'crowds',
    beanstalk_host = 'localhost',
    beanstalk_port = 11300,
    log_dir = 'logs',
    lucene_index_dir = '/tmp/twitter_search',
    pdb = pdb.set_trace,
)

try:
    from etc.settings_local import settings as _s
    settings.update(_s)
except ImportError:
    pass
