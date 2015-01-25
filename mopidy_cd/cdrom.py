from __future__ import unicode_literals

import logging
import time
import discid

logger = logging.getLogger(__name__)

class Cdrom(object):

    def __init__(self):
        self.refresh()
    
    def refresh(self):
        self.disc = discid.read()
        logger.debug("Cdrom: reading cd")
        self.n = len(self.disc.tracks)
        logger.debug('Cdrom: %d tracks found',self.n)
        self.tracks=[]
        for track in self.disc.tracks:
            number = track.number
            duration = track.seconds
            name = 'Cdrom Track %s (%s)' % (number, time.strftime('%H:%M:%S', time.gmtime (duration)))
            self.tracks.append((number,name,duration))
