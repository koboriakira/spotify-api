from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track

class CurrentPlayingUsecase:
    def __init__(self):
        self.spotipy = Spotipy.get_instance()

    def get_current_playing(self) -> Optional[Track]:
        return self.spotipy.get_current_playing()
