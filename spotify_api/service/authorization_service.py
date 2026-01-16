from datetime import datetime as DateTime

from custom_logger import get_logger
from domain.infrastructure.token_info_repository import TokenInfoRepository
from infrastructure.spotify_oauth import SpotifyOauth

logger = get_logger(__name__)


class AuthorizationService:
    def __init__(self, token_repository: TokenInfoRepository):
        self.token_repository = token_repository
        self.spotify_oauth = SpotifyOauth()

    def get_access_token(self) -> str:
        token_info = self.token_repository.load()
        if token_info is None:
            raise Exception("token_info is not found")

        expires_at = token_info["expires_at"]
        if expires_at < DateTime.now().timestamp():
            # 期限切れの場合はリフレッシュトークンを使ってアクセストークンを更新する
            token_info = self.spotify_oauth.refresh_access_token(token_info["refresh_token"])
            self.token_repository.save(token_info=token_info)
        return token_info["access_token"]
