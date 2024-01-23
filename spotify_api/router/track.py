from typing import Optional
from fastapi import APIRouter, Header
from interface.track_response import TrackResponse
from interface import track
from util.environment import Environment

router = APIRouter()


@router.get("/{track_id}", response_model=Optional[TrackResponse],)
def get_track(track_id: str,
              access_token: Optional[str] = Header(None)):
    """
    指定した曲を取得する
    """
    Environment.valid_access_token(access_token)
    return track.get_track(track_id=track_id)



@router.post("/{track_id}/love", response_model=dict)
async def love_track(track_id: str,
                     access_token: Optional[str] = Header(None)):
    """
    指定した曲を「いいね」する
    """
    Environment.valid_access_token(access_token)
    track.love_track(track_id=track_id)
    return {
        "is_success": True,
    }
