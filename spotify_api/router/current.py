from typing import Optional
from fastapi import APIRouter, Header
from interface.track_response import TrackResponse
from interface import track
from util.environment import Environment

router = APIRouter()


@router.get("/playing", response_model=Optional[TrackResponse])
async def get_current_playing(access_token: Optional[str] = Header(None)):
    """
    現在流れている曲を取得する
    """
    Environment.valid_access_token(access_token)
    return track.get_current_playing()
