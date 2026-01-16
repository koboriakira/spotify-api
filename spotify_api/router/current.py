from fastapi import APIRouter, Header
from interface import track
from util.environment import Environment

from router.response import BaseResponse, TrackResponse
from router.response.track_response_translator import TrackResponseTranslator

router = APIRouter()


@router.get("/playing", response_model=TrackResponse | BaseResponse)
async def get_current_playing(access_token: str | None = Header(None)):
    """
    現在流れている曲を取得する
    """
    Environment.valid_access_token(access_token)
    track_model = track.get_current_playing()
    if track_model is None:
        return BaseResponse(message="no track is playing now.")
    data = TrackResponseTranslator.to_entity(track_model)
    return TrackResponse(data=data)


@router.post("/playing", response_model=BaseResponse)
async def post_current_playing(access_token: str | None = Header(None)):
    """
    現在流れている曲を取得して、Slackに通知する
    """
    Environment.valid_access_token(access_token)
    track.post_current_playing()
    return BaseResponse()
