from __future__ import absolute_import, unicode_literals

import logging
import math

import musicbrainzngs

from collections.abc import Mapping
from collections import namedtuple
from datetime import timedelta

from mopidy.audio.scan import Scanner
from mopidy.exceptions import ScannerError

from . import Extension


logger = logging.getLogger(__name__)

Artist = namedtuple('Artist', 'id name sortname')
Track = namedtuple('Track', 'id title number disc_number duration artists')
Disc = namedtuple('Disc', 'id discid title year discs artists images tracks')

CD_PROTOCOL = 'cdda://'
UNKNOWN_DISC = Disc(None, None, 'Unknown CD', '', 1, (), (), ())


musicbrainzngs.set_useragent(Extension.dist_name, Extension.version)


class DiscID(object):

    id = None
    toc = ''
    tracks = ()

    def __init__(self):
        try:
            # see GstAudioCdSrc docs for emitted tags
            tags = Scanner().scan(uri=CD_PROTOCOL).tags
            toc = [
                int(i, 16) for i in tags['musicbrainz-discid-full'][0].split()
            ]
            offsets = toc[3:] + toc[2:3]

            self.id = tags['musicbrainz-discid'][0]
            self.toc = ' '.join(str(i) for i in toc)
            self.tracks = [
                (i + 1, DiscID._to_seconds(offsets[i + 1] - offsets[i]))
                for i in range(len(offsets) - 1)
            ]
        except (LookupError, ScannerError) as e:
            logger.info('Error identifying disc: %s', e)

    @staticmethod
    def _to_seconds(sectors):
        return int(math.floor(sectors / 75.0 + 0.5))


class CdRom(object):

    disc = UNKNOWN_DISC

    def read(self):
        discid = DiscID()
        if discid.id:
            logger.debug(
                'Read disc: MusicBrainz DiscID %s, %d tracks',
                discid.id, len(discid.tracks)
            )
        else:
            self.disc = UNKNOWN_DISC
            return

        # use cached disc info if possible
        if self.disc.discid == discid.id:
            return

        try:
            mbrainz_info = musicbrainzngs.get_releases_by_discid(
                id=discid.id,
                toc=discid.toc,
                includes=['artist-credits', 'recordings'],
                cdstubs=False
            )
            # mbrainz_info is either
            # a {disc: {release-list: [...]}, ...} dict or
            # a {release-list: [...]} dict when matched by ToC
            release = mbrainz_info.get('disc', mbrainz_info)['release-list'][0]
            try:
                images = musicbrainzngs.get_image_list(release['id'])
            except musicbrainzngs.ResponseError as e:
                logger.debug('Error getting CD images from MusicBrainz: %s', e)
                images = {'images': ()}

            self.disc = Disc(
                id=release['id'],
                discid=discid.id,
                title=release['title'],
                discs=release['medium-count'],
                year=release['date'],
                images=CdRom._extract_images(images['images']),
                artists=CdRom._extract_artists(release['artist-credit']),
                tracks=CdRom._extract_tracks(discid, release['medium-list'])
            )
        except (LookupError, musicbrainzngs.WebServiceError) as e:
            logger.info('Error accessing MusicBrainz: %s', e)
            self.disc = UNKNOWN_DISC._replace(
                discid=discid.id,
                tracks=CdRom._extract_tracks(discid)
            )

    @staticmethod
    def _extract_artists(artist_credits):
        return {
            CdRom._make_artist(credit)
            for credit in artist_credits
            if isinstance(credit, Mapping)
        }

    @staticmethod
    def _extract_images(images_list):
        return {
            image['image']
            for image in images_list
            if image['front'] or image['back']
        }

    @staticmethod
    def _extract_tracks(discid, medium_list=()):
        def match_by_discid(medium):
            if medium.get('format', '').lower() != 'cd':
                return False
            return any(disc['id'] == discid.id for disc in medium['disc-list'])

        cd = next(
            (medium for medium in medium_list if match_by_discid(medium)),
            None
        )
        if cd:
            disc_num = int(cd['position'])
            tracks = cd['track-list']
            return [CdRom._make_track_mbrainz(disc_num, tr) for tr in tracks]
        else:
            return [CdRom._make_track_discid(track) for track in discid.tracks]

    @staticmethod
    def _make_artist(artist_dict):
        artist = artist_dict['artist']
        return Artist(
            id=artist['id'],
            name=artist['name'],
            sortname=artist['sort-name']
        )

    @staticmethod
    def _make_track_mbrainz(disc_number, track):
        recording = track['recording']
        return Track(
            id=track['id'],
            title=recording['title'],
            number=int(track['number']),
            disc_number=disc_number,
            duration=int(track['length']),
            artists=CdRom._extract_artists(recording['artist-credit'])
        )

    @staticmethod
    def _make_track_discid(track):
        return Track(
            id=None,
            title='CD Track %d (%s)' % (track[0], timedelta(seconds=track[1])),
            number=track[0],
            disc_number=1,
            duration=track[1] * 1000,
            artists=()
        )
