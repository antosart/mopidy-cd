from __future__ import absolute_import, unicode_literals

import logging

import pykka

from mopidy import backend
from mopidy.models import Album, Artist, Image, Ref, Track

from . import Extension
from .cdrom import CdRom, CD_PROTOCOL


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
        track_number = int(uri.lstrip(ROOT_URI))
        logger.debug('CD track #%d selected', track_number)

        disc = self.cdrom.disc
        track = disc.tracks[track_number - 1]
        return [
            Track(
                uri=uri, musicbrainz_id=track.id,
                name=track.title, length=track.duration,
                track_no=track.number, disc_no=track.disc_number,
                artists={CdLibrary._make_artist(ar) for ar in track.artists},
                album=Album(
                    musicbrainz_id=disc.id, name=disc.title, date=disc.year,
                    num_discs=disc.discs, num_tracks=len(disc.tracks),
                    artists={CdLibrary._make_artist(ar) for ar in disc.artists}
                )
            )
        ]

    def get_images(self, uris):
        images = {Image(uri=img) for img in self.cdrom.disc.images}
        return {uri: images for uri in uris}

    def refresh(self, uri=None):
        self.cdrom.read()

    @staticmethod
    def _make_artist(artist_tuple):
        return Artist(
            musicbrainz_id=artist_tuple.id,
            name=artist_tuple.name,
            sortname=artist_tuple.sortname
        )


class CdPlayback(backend.PlaybackProvider):

    def translate_uri(self, uri):
        return uri.replace(ROOT_URI, CD_PROTOCOL)
