from __future__ import unicode_literals

import logging
import os

import pygst
pygst.require('0.10')
import gst
import gobject

from mopidy import config, exceptions, ext


__version__ = '0.1'

# If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)

class Extension(ext.Extension):

    dist_name = 'Mopidy-Cd'
    ext_name = 'cd'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def setup(self, registry):
        # Register a backend
        from .backend import CdBackend
        registry.add('backend', CdBackend)
