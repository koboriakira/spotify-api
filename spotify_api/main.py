import os
from typing import Optional
from mangum import Mangum
from fastapi import FastAPI, Header, Response, Request, HTTPException
from spotipy.oauth2 import SpotifyOAuth
from custom_logger import get_logger
# from interface.track_response import TrackResponse
# from interface import track
from cache import Cache

logger = get_logger(__name__)
logger.info("start")
logger.debug("debug: ON")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SCOPE = 'user-library-read,user-top-read,user-read-currently-playing'
ENVIRONMENT = os.environ.get("ENVIRONMENT")


def valid_saccess_token(secret: str) -> None:
    if ENVIRONMENT == "dev":
        return
    # SPOTIFY_CLIENT_SECRETを使って、アクセストークンを検証する
    if secret != SPOTIFY_CLIENT_SECRET:
        raise Exception("invalid secret: " + secret)

def get_callback_url() -> str:
    """ 認証のコールバック用URLを取得 """
    # NOTE: 返却値が変わる場合は、Spotifyのアプリ設定画面のRedirect URIsも変更する必要がある
    path = "authorize_callback"
    if ENVIRONMENT == "dev":
        return f"http://localhost:10120/{path}"
    else:
        return f"https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/{path}"

app = FastAPI(
    title="My Spotify API",
    version="0.0.1",
)

@app.get("/authorize", status_code=303)
def authorize():
    """ Spotifyの認証ページにリダイレクト """
    sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=get_callback_url(),
                    scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    logger.info(auth_url)
    return Response(headers={"Location": auth_url}, status_code=303)

@app.get("/authorize_callback", response_model=dict)
async def authorize_callback(request: Request):
    """
    Spotifyの認証後のコールバック用URL。
    get_access_token() -> Spotifyの認証画面 -> authorize_callback()とリダイレクトされる。
    """
    global cache

    # 認証コードを取得
    code = request.query_params.get('code')
    if code is None:
        raise HTTPException(status_code=400, detail="code is not found.")

    sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=get_callback_url(),
                    scope=SCOPE)
    token_info = sp_oauth.get_access_token(code)
    Cache.write_token_info(token_info)
    return token_info


# @app.get("/track/{track_id}", response_model=Optional[TrackResponse],)
# def get_track(track_id: str,
#               accsses_token: str = Header(None)):
#     # valid_saccess_token(accsses_token)
#     return track.get_track(track_id=track_id)


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

@app.get("/check_access_token")
def hello():
    return {
        'access_token': Cache.get_access_token(),
    }


handler = Mangum(app, lifespan="off")
