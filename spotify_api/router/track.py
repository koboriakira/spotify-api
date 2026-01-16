from fastapi import APIRouter, Header
from interface import track
from router.response import BaseResponse, TrackResponse
from router.response.track_response_translator import TrackResponseTranslator
from util.environment import Environment

router = APIRouter()


@router.get("/{track_id}", response_model=TrackResponse)
def get_track(track_id: str, access_token: str | None = Header(None)):
    """
    指定した曲を取得する
    """
    Environment.valid_access_token(access_token)
    track_model = track.get_track(track_id=track_id)
    data = TrackResponseTranslator.to_entity(track_model) if track_model is not None else None
    return TrackResponse(data=data)


@router.post("/{track_id}/love", response_model=BaseResponse)
async def love_track(track_id: str, access_token: str | None = Header(None)):
    """
    指定した曲を「いいね」する
    """
    Environment.valid_access_token(access_token)
    response = track.love_track(track_id=track_id)
    return BaseResponse(data={"result": response.result.value})
