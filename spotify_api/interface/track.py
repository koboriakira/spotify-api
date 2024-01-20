from infrastructure.spotipy import Spotipy
from interface.track_response_translator import TrackResponseTranslator
from interface.track_response import TrackResponse
from typing import Optional
from custom_logger import get_logger
from usecase.get_track_usecase import GetTrackUsecase

def get_track(track_id: str) -> Optional[TrackResponse]:
    get_track_usecase = GetTrackUsecase()
    track = get_track_usecase.execute(track_id=track_id)
    if track is None:
        return None
    return TrackResponseTranslator.to_entity(track)
