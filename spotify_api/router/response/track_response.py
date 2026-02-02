from pydantic import BaseModel, Field
from .base_response import BaseResponse


class Track(BaseModel):
    id: str = Field(description="Spotify ID of the track")
    name: str = Field(description="Name of the track")
    artists: list[str] = Field(description="Name of the artist")
    spotify_url: str = Field(description="Spotify URL of the track")
    cover_url: str = Field(description="Cover URL of the track")
    release_date: str | None = Field(description="Release date of the track", default=None)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Track):
            return NotImplemented
        return self.id == other.id


class TrackResponse(BaseResponse):
    data: Track = Field(description="Track data")
