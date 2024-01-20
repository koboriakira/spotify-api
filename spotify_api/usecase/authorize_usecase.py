from typing import Optional
from infrastructure.spotipy import Spotipy
from custom_logger import get_logger

logger = get_logger(__name__)

class AuthorizeUsecase:
    def get_authorize_url(self) -> str:
        authorize_url = Spotipy.get_authorize_url()
        logger.info("authorize_url: " + authorize_url)
        return authorize_url

    def authorize_callback(self, code: str) -> dict:
        token_info = Spotipy.authorize_callback(code=code)
        return token_info
