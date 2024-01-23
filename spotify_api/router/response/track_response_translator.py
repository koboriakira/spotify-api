from datetime import date as DateObject
from domain.model.track import Track as TrackEntity
from router.response.track_response import Track

class TrackResponseTranslator:
    @staticmethod
    def to_entity(track: TrackEntity) -> Track:
        release_date = None
        if track.album["release_date"] is not None:
            # YYYY-MM-DD形式じゃない可能性があるので、例外処理する
            try:
                release_date = DateObject.fromisoformat(track.album["release_date"]).isoformat()
            except:
                pass
        return Track(
            id=track.id,
            name=track.name,
            artists=[artist["name"] for artist in track.artists],
            spotify_url=track.spotify_url,
            cover_url=track.album["images"][0]["url"],
            release_date=release_date
        )
