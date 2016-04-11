from __future__ import unicode_literals

import logging
import time
import discid

try:
    import musicbrainzngs
    musicbrainz = True
except:
    musicbrainz = False
    
logger = logging.getLogger(__name__)

class Cdrom(object):

    def __init__(self):
        self.refresh()
    
    def refresh(self):
        self.tracks=[]
        try:
            self.disc = discid.read()
        except:
            logger.debug("Cdrom: Unable to read cd")
            return
        logger.debug("Cdrom: reading cd")
        self.n = len(self.disc.tracks)
        logger.debug('Cdrom: %d tracks found',self.n)
        if musicbrainz:
            musicbrainzngs.set_useragent("Audacious", "0.1", "https://github.com/jonnybarnes/audacious")
            try:
                result = musicbrainzngs.get_releases_by_discid(self.disc.id, includes=["artists", "recordings"])
            except musicbrainzngs.ResponseError:
                logger.debug("Disc not found on Musicbrainz")
            else:
                # mbtracks = result["disc"]["release-list"][0]["medium-list"][0]["track-list"]
                mbtracks = result["cdstub"]["track-list"]
                if len(mbtracks) == len(self.disc.tracks):
                    for mbtrack, track in zip(mbtracks,self.disc.tracks):
                        number = track.number
                        duration = track.seconds
                        name = '%s - %s (%s)' % (number, mbtrack["title"], time.strftime('%H:%M:%S', time.gmtime (duration)))
                        self.tracks.append((number,name,duration))
                    return
        for track in self.disc.tracks:
            number = track.number
            duration = track.seconds
            name = 'Cdrom Track %s (%s)' % (number, time.strftime('%H:%M:%S', time.gmtime (duration)))
            self.tracks.append((number,name,duration))
