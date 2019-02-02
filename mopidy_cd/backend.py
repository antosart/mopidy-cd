from __future__ import absolute_import, unicode_literals

import logging

import pykka

from mopidy import backend
from mopidy.models import Album, Artist, Image, Ref, SearchResult, Track

from . import Extension
from .cdrom import CD_PROTOCOL, UNKNOWN_DISC, CdRom


logger = logging.getLogger(__name__)

ROOT_URI = 'cd:/'


class CdBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = [Extension.ext_name]

    def __init__(self, config, audio):
        super(CdBackend, self).__init__()
        self.library = CdLibrary(backend=self)
        self.playback = CdPlayback(audio=audio, backend=self)


class CdLibrary(backend.LibraryProvider):

    root_directory = Ref.directory(uri=ROOT_URI, name='CD')
    cdrom = CdRom()

    def browse(self, uri):
        self.refresh()

        return [
            Ref.track(uri=ROOT_URI + str(track.number), name=track.title)
            for track in self.cdrom.disc.tracks
        ]

    def lookup(self, uri):
        disc = self.cdrom.disc
        album = CdLibrary._make_album(disc)
        track_path = uri.lstrip(ROOT_URI)
        if track_path:
            try:
                track_number = int(track_path)
            except ValueError as e:
                logger.warning('Invalid uri %s: %s', uri, e)
                return []
            else:
                logger.debug('CD track #%d selected', track_number)
                track = disc.tracks[track_number - 1]
                return [self._make_track(album, track)]
        else:
            logger.debug('All CD tracks selected')
            return [self._make_track(album, track) for track in disc.tracks]

    def get_images(self, uris):
        images = {Image(uri=img) for img in self.cdrom.disc.images}
        return {uri: images for uri in uris}

    def refresh(self, uri=None):
        self.cdrom.read()

    def search(self, query=None, uris=None, exact=False):
        def match(subvalue, value):
            if exact:
                return subvalue == value
            else:
                return subvalue.lower() in value.lower()

        if uris and all(uri not in ROOT_URI for uri in uris):
            return None

        self.refresh()

        disc = self.cdrom.disc
        if disc == UNKNOWN_DISC:
            return None

        any_query = query.get('any')
        album_query = query.get('album') or any_query or ()
        artist_query = query.get('artist') or any_query or ()
        track_name_query = query.get('track_name') or any_query or ()

        disc_album = CdLibrary._make_album(disc)
        return SearchResult(
            albums=[disc_album] if any(
                match(album, disc_album.name)
                for album in album_query
            ) else (),
            artists=[
                disc_artist
                for disc_artist in disc_album.artists
                if any(
                    match(artist, disc_artist.name)
                    for artist in artist_query
                )
            ],
            tracks=[
                CdLibrary._make_track(disc_album, track)
                for track in disc.tracks
                if any(
                    match(track_name, track.title)
                    for track_name in track_name_query
                )
            ]
        )

    @staticmethod
    def _make_album(disc):
        return Album(
            uri=ROOT_URI,
            musicbrainz_id=disc.id,
            name=disc.title,
            date=disc.year,
            artists={CdLibrary._make_artist(ar) for ar in disc.artists},
            images=disc.images,
            num_discs=disc.discs,
            num_tracks=len(disc.tracks)
        )

    @staticmethod
    def _make_artist(artist_tuple):
        return Artist(
            uri=ROOT_URI,
            musicbrainz_id=artist_tuple.id,
            name=artist_tuple.name,
            sortname=artist_tuple.sortname
        )

    @staticmethod
    def _make_track(album, track_tuple):
        return Track(
            uri=ROOT_URI + str(track_tuple.number),
            musicbrainz_id=track_tuple.id,
            name=track_tuple.title,
            length=track_tuple.duration,
            track_no=track_tuple.number,
            disc_no=track_tuple.disc_number,
            album=album,
            artists={CdLibrary._make_artist(ar) for ar in track_tuple.artists}
        )


class CdPlayback(backend.PlaybackProvider):

    def translate_uri(self, uri):
        return uri.replace(ROOT_URI, CD_PROTOCOL)
