from typing import Optional
from fastapi import APIRouter, Header
from interface import track
from util.environment import Environment
from router.response import TrackResponse
from router.response.track_response_translator import TrackResponseTranslator

router = APIRouter()


@router.get("/playing", response_model=Optional[TrackResponse])
async def get_current_playing(access_token: Optional[str] = Header(None)):
    """
    現在流れている曲を取得する
    """
    Environment.valid_access_token(access_token)
    track_model = track.get_current_playing()
    data = TrackResponseTranslator.to_entity(track_model) if track_model is not None else None
    return TrackResponse(data=data)
