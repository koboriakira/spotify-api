from typing import Optional
from custom_logger import get_logger
from usecase.get_track_usecase import GetTrackUsecase
from usecase.current_playing_usecase import CurrentPlayingUsecase
from usecase.love_track_usecase import LoveTrackUsecase, LoveTrackResponse
from infrastructure.token_info_s3_repository import TokenInfoS3Repository
from infrastructure.token_info_local_repository import TokenInfoLocalRepository
from service.authorization_service import AuthorizationService
from util.environment import Environment
from domain.model.track import Track

if Environment.is_dev() or Environment.is_local():
    repository = TokenInfoLocalRepository()
else:
    repository = TokenInfoS3Repository()
authorization_service = AuthorizationService(token_repository=repository)


def get_track(track_id: str) -> Optional[Track]:
    get_track_usecase = GetTrackUsecase(authorization_service=authorization_service)
    return get_track_usecase.execute(track_id=track_id)


def get_current_playing() -> Optional[Track]:
    current_playing_usecase = CurrentPlayingUsecase(
        authorization_service=authorization_service
    )
    return current_playing_usecase.get_current_playing()


def post_current_playing() -> bool:
    current_playing_usecase = CurrentPlayingUsecase(
        authorization_service=authorization_service
    )
    return current_playing_usecase.notificate_current_playing()


def love_track(track_id: str) -> LoveTrackResponse:
    love_track_usecase = LoveTrackUsecase(authorization_service=authorization_service)
    return love_track_usecase.execute(track_id=track_id)
