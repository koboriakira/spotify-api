from custom_logger import get_logger
from domain.infrastructure.token_info_repository import TokenInfoRepository
from infrastructure.spotify_oauth import SpotifyOauth

logger = get_logger(__name__)


class AuthorizeUsecase:
    def __init__(self, repository: TokenInfoRepository):
        self.repository = repository
        self.spotify_oauth = SpotifyOauth()

    def get_authorize_url(self) -> str:
        authorize_url = self.spotify_oauth.get_authorize_url()
        logger.info("authorize_url: " + authorize_url)
        return authorize_url

    def authorize_callback(self, code: str) -> dict:
        token_info = self.spotify_oauth.authorize_callback(code=code)
        self.repository.save(token_info=token_info)
        return token_info
