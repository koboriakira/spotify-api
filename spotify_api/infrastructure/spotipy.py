import spotipy
from typing import Optional
from domain.model.track import Track
from domain.track_translator import TrackTranslator
from custom_logger import get_logger

logger = get_logger(__name__)

class Spotipy:
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp

    @classmethod
    def get_instance(cls, access_token: str) -> 'Spotipy':
        logger.debug("access_token: {}".format(access_token))
        return cls(spotipy.Spotify(auth=access_token))

    def current_user_recently_played(self) -> list:
        raise NotImplementedError()

    def get_track(self, track_id: str) -> Optional[Track]:
        track_entity = self.sp.track(track_id=track_id)
        logger.debug(track_entity)
        if track_entity is None:
            return None
        return TrackTranslator.from_entity(track_entity)

    def get_current_playing(self) -> Optional[Track]:
        playing_track = self.sp.current_user_playing_track()
        if playing_track is None:
            return None
        logger.debug(playing_track)
        return TrackTranslator.from_entity(playing_track["item"])

    def love_track(self, track_id: str) -> None:
        logger.debug(track_id)
        response = self.sp.current_user_saved_tracks_add(tracks=[track_id])
        logger.debug(response)

    def get_album(self, album_id: str):
        raise NotImplementedError()
