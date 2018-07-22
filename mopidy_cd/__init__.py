from __future__ import unicode_literals

import os

from mopidy import config, ext


__version__ = '0.4'


class Extension(ext.Extension):

    dist_name = 'Mopidy-Cd'
    ext_name = 'cd'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def setup(self, registry):
        from .backend import CdBackend
        registry.add('backend', CdBackend)
