from ..domain.model.track import Track
from ..infrastructure.spotipy import Spotipy
from ..service.authorization_service import AuthorizationService


class GetTrackUsecase:
    def __init__(self, authorization_service: AuthorizationService):
        access_token = authorization_service.get_access_token()
        self.spotipy = Spotipy.get_instance(access_token=access_token)

    def execute(self, track_id: str) -> Track | None:
        return self.spotipy.get_track(track_id)
