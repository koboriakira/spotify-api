from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track
from domain.infrastructure.token_info_repository import TokenInfoRepository

class GetTrackUsecase:
    def __init__(self, token_repository: TokenInfoRepository):
        token_info = token_repository.load()
        self.spotipy = Spotipy.get_instance(token_info=token_info)

    def execute(self, track_id: str) -> Optional[Track]:
        return self.spotipy.get_track(track_id)
