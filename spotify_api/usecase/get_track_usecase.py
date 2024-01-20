from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track

class GetTrackUsecase:
    def __init__(self):
        self.spotipy = Spotipy.get_instance()

    def execute(self, track_id: str) -> Optional[Track]:
        return self.spotipy.get_track(track_id)
