from pydantic import BaseModel, Field
from typing import Optional

class TrackResponse(BaseModel):
    id: str = Field(description="Spotify ID of the track")
    name: str = Field(description="Name of the track")
    artists: list[str] = Field(description="Name of the artist")
    spotify_url: str = Field(description="Spotify URL of the track")
    cover_url: str = Field(description="Cover URL of the track")
    release_date: Optional[str] = Field(description="Release date of the track", default=None)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, __value: 'TrackResponse') -> bool:
        return self.id == __value.id
