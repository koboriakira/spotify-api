from interface.track_response_translator import TrackResponseTranslator
from interface.track_response import TrackResponse
from typing import Optional
from custom_logger import get_logger
from usecase.get_track_usecase import GetTrackUsecase
from usecase.current_playing_usecase import CurrentPlayingUsecase
from infrastructure.token_info_s3_repository import TokenInfoS3Repository
from service.authorization_service import AuthorizationService

repository = TokenInfoS3Repository()
authorization_service = AuthorizationService(token_repository=repository)

def get_track(track_id: str) -> Optional[TrackResponse]:
    get_track_usecase = GetTrackUsecase(authorization_service=authorization_service)
    track = get_track_usecase.execute(track_id=track_id)
    if track is None:
        return None
    return TrackResponseTranslator.to_entity(track)

def get_current_playing() -> Optional[TrackResponse]:
    current_playing_usecase = CurrentPlayingUsecase(authorization_service=authorization_service)
    track = current_playing_usecase.get_current_playing()
    if track is None:
        return None
    return TrackResponseTranslator.to_entity(track)

def post_current_playing() -> dict:
    current_playing_usecase = CurrentPlayingUsecase(authorization_service=authorization_service)
    return current_playing_usecase.notificate_current_playing()
