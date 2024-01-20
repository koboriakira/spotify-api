import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional
from datetime import datetime as DatetimeObject
from datetime import timedelta
from domain.model.track import Track
from domain.track_translator import TrackTranslator
from cache import Cache
from custom_logger import get_logger

logger = get_logger(__name__)

class Spotipy:

    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SCOPE = 'user-library-read,user-top-read,user-read-currently-playing'

    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp

    @classmethod
    def get_instance(cls) -> 'Spotipy':
        access_token = Cache.get_access_token()
        if access_token:
            return cls(spotipy.Spotify(auth=access_token))

        # 以下はアクセストークンが期限切れの場合の処理
        refresh_token = Cache.get_refresh_token()
        sp_oauth = SpotifyOAuth(client_id=cls.CLIENT_ID,
                        client_secret=cls.CLIENT_SECRET,
                        redirect_uri=cls.get_callback_url(),
                        scope=cls.SCOPE)
        token_info = sp_oauth.refresh_access_token(refresh_token)
        Cache.write_token_info(token_info)
        access_token = token_info['access_token']
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

    def get_album(self, album_id: str):
        raise NotImplementedError()
