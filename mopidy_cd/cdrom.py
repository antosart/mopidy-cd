from __future__ import unicode_literals

import logging

import discid
import musicbrainzngs

from collections import Mapping, namedtuple
from datetime import timedelta
from itertools import ifilter, imap

from . import Extension


logger = logging.getLogger(__name__)

Artist = namedtuple('Artist', 'id name sortname')
Track = namedtuple('Track', 'id title number disc_number duration artists')
Disc = namedtuple('Disc', 'id discid title year discs artists images tracks')

UNKNOWN_DISC = Disc(None, None, 'Unknown CD', '', 1, (), (), ())


class CdRom(object):

    disc = UNKNOWN_DISC

    def __init__(self):
        musicbrainzngs.set_useragent(
            Extension.dist_name,
            Extension.version
        )

    def read(self):
        try:
            disc_id = discid.read()
            logger.debug(
                'Read disc: MusicBrainz DiscID %s, FreeDB ID %s, %d tracks',
                disc_id.id,
                disc_id.freedb_id,
                len(disc_id.tracks)
            )
        except (discid.DiscError, NotImplementedError) as e:
            logger.info('Error identifying disc: %s', e)
            self.disc = UNKNOWN_DISC
            return

        # use cached disc info if possible
        if self.disc.discid == disc_id.id:
            return

        try:
            mbrainz_info = musicbrainzngs.get_releases_by_discid(
                id=disc_id.id,
                toc=disc_id.toc_string,
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
                discid=disc_id.id,
                title=release['title'],
                discs=release['medium-count'],
                year=release['date'],
                images=CdRom._extract_images(images['images']),
                artists=CdRom._extract_artists(release['artist-credit']),
                tracks=CdRom._extract_tracks(disc_id, release['medium-list'])
            )
        except (LookupError, musicbrainzngs.WebServiceError) as e:
            logger.info('Error accessing MusicBrainz: %s', e)
            self.disc = UNKNOWN_DISC._replace(
                discid=disc_id.id,
                tracks=CdRom._extract_tracks(disc_id)
            )

    @staticmethod
    def _extract_artists(artist_credits):
        artist_dicts = ifilter(
            lambda credit: isinstance(credit, Mapping), artist_credits
        )
        return set(imap(CdRom._make_artist, artist_dicts))

    @staticmethod
    def _extract_images(images_list):
        front_back_images = ifilter(
            lambda image: image['front'] or image['back'], images_list
        )
        return set(imap(lambda image: image['image'], front_back_images))

    @staticmethod
    def _extract_tracks(discid, medium_list=()):
        def match_by_discid(medium):
            if medium['format'].lower() != 'cd':
                return False
            return any(disc['id'] == discid.id for disc in medium['disc-list'])

        cd = next(ifilter(match_by_discid, medium_list), None)
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
            title='CD Track %d (%s)' % (
                track.number, timedelta(seconds=track.seconds)
            ),
            number=track.number,
            disc_number=1,
            duration=track.seconds * 1000,
            artists=()
        )
