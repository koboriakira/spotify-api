from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track
from service.authorization_service import AuthorizationService
from enum import Enum
from dataclasses import dataclass


class LoveTrackResult(Enum):
    SUCCESS = "success"
    ALREADY_LOVED = "already_loved"
    FAILED = "failed"


@dataclass(frozen=True)
class LoveTrackResponse:
    result: LoveTrackResult


class LoveTrackUsecase:
    def __init__(self, authorization_service: AuthorizationService) -> None:
        access_token = authorization_service.get_access_token()
        self.spotipy = Spotipy.get_instance(access_token=access_token)

    def execute(self, track_id: str) -> LoveTrackResponse:
        if self.spotipy.is_track_saved(track_id):
            return LoveTrackResponse(result=LoveTrackResult.ALREADY_LOVED)
        self.spotipy.love_track(track_id)
        return LoveTrackResponse(result=LoveTrackResult.SUCCESS)
