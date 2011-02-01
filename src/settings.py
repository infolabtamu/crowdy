import pdb
class SettingsBunch(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

settings = SettingsBunch(
    log_dir = 'logs',
    pdb = pdb.set_trace,
)

try:
    from settings_prod import settings as s
except:
    from settings_dev import settings as s
settings.update(s)
