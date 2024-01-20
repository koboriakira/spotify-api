from infrastructure.spotipy import Spotipy
from interface.track_response_translator import TrackResponseTranslator
from interface.track_response import TrackResponse
from typing import Optional
from custom_logger import get_logger
from usecase.get_track_usecase import GetTrackUsecase
from usecase.current_playing_usecase import CurrentPlayingUsecase

def get_track(track_id: str) -> Optional[TrackResponse]:
    get_track_usecase = GetTrackUsecase()
    track = get_track_usecase.execute(track_id=track_id)
    if track is None:
        return None
    return TrackResponseTranslator.to_entity(track)

def get_current_playing() -> Optional[TrackResponse]:
    current_playing_usecase = CurrentPlayingUsecase()
    track = current_playing_usecase.get_current_playing()
    if track is None:
        return None
    return TrackResponseTranslator.to_entity(track)

def post_current_playing() -> None:
    current_playing_usecase = CurrentPlayingUsecase()
    current_playing_usecase.notificate_current_playing()
