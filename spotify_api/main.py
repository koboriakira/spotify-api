import os
from typing import Optional
from mangum import Mangum
from fastapi import FastAPI, Header, Response, Request, HTTPException
from custom_logger import get_logger
from interface.track_response import TrackResponse
from interface import track, authorize

logger = get_logger(__name__)
logger.info("start")
logger.debug("debug: ON")

SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
ENVIRONMENT = os.environ.get("ENVIRONMENT")


def valid_saccess_token(secret: str) -> None:
    if ENVIRONMENT == "dev":
        return
    # SPOTIFY_CLIENT_SECRETを使って、アクセストークンを検証する
    if secret != SPOTIFY_CLIENT_SECRET:
        raise Exception("invalid secret: " + secret)

app = FastAPI(
    title="My Spotify API",
    version="0.0.1",
)

@app.get("/authorize", status_code=303)
def get_authorize():
    """ Spotifyの認証ページにリダイレクト """
    authorize_url = authorize.get_authorize_url()
    return Response(headers={"Location": authorize_url}, status_code=303)

@app.get("/authorize_callback", response_model=dict)
async def authorize_callback(request: Request):
    """
    Spotifyの認証後のコールバック用URL。
    get_authorize() -> Spotifyの認証画面 -> authorize_callback()とリダイレクトされる。
    """
    code = request.query_params.get('code')
    if code is None:
        raise HTTPException(status_code=400, detail="code is not found.")
    return authorize.authorize_callback(code=code)

@app.get("/track/{track_id}", response_model=Optional[TrackResponse],)
def get_track(track_id: str,
              accsses_token: str = Header(None)):
    # valid_saccess_token(accsses_token)
    return track.get_track(track_id=track_id)



@app.get("/current/playing", response_model=Optional[TrackResponse])
async def get_current_playing():
    """
    現在流れている曲を取得する
    """
    return track.get_current_playing()


@app.post("/current/playing", response_model=bool)
async def post_current_playing():
    """
    現在流れている曲を取得して、Slackに通知する
    """
    try:
        track.post_current_playing()
        return True
    except Exception as e:
        logger.error(e)
        return False


@app.get("/healthcheck")
def hello():
    """
    Return a greeting
    """
    logger.debug("healthcheck")
    logger.info("healthcheck")
    return {
        'status': 'ok',
    }


handler = Mangum(app, lifespan="off")
