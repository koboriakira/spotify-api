from domain.model.track import Track
from interface.track_response import TrackResponse
from datetime import date as DateObject

class TrackResponseTranslator:
    @staticmethod
    def to_entity(track: Track) -> TrackResponse:
        release_date = None
        if track.album["release_date"] is not None:
            # YYYY-MM-DD形式じゃない可能性があるので、例外処理する
            try:
                release_date = DateObject.fromisoformat(track.album["release_date"]).isoformat()
            except:
                pass
        return TrackResponse(
            id=track.id,
            name=track.name,
            artists=[artist["name"] for artist in track.artists],
            spotify_url=track.spotify_url,
            cover_url=track.album["images"][0]["url"],
            release_date=release_date
        )
