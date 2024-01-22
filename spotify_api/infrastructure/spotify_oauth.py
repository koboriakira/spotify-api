import os
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SCOPE = 'user-library-read,user-top-read,user-read-currently-playing'

def get_callback_url(cls) -> str:
    """ 認証のコールバック用URLを取得 """
    # NOTE: 返却値が変わる場合は、Spotifyのアプリ設定画面のRedirect URIsも変更する必要がある
    path = "authorize_callback"
    if os.getenv('ENVIRONMENT') == "dev":
        return f"http://localhost:10120/{path}"
    else:
        return f"https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/{path}"


class SpotifyOauth:
    def __init__(self):
        self.sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                                     client_secret=CLIENT_SECRET,
                                     redirect_uri=get_callback_url(),
                                     scope=SCOPE)

    def get_authorize_url(self) -> str:
        """
        認証用のURLを取得
        """
        return self.sp_oauth.get_authorize_url()

    def authorize_callback(self, code: str) -> dict:
        """
        認証コールバック
        token_infoを返す
        """
        return self.sp_oauth.get_access_token(code)

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        アクセストークンをリフレッシュ
        token_infoを返す
        """
        return self.sp_oauth.refresh_access_token(refresh_token)
