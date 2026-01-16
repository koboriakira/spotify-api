from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    album: dict
    artists: list
    available_markets: list
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: dict
    external_urls: dict
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: str | None
    track_number: int
    type: str
    uri: str

    @staticmethod
    def from_dict(obj: dict) -> "Track":
        album = obj["album"]
        artists = obj["artists"]
        available_markets = obj["available_markets"]
        disc_number = obj["disc_number"]
        duration_ms = obj["duration_ms"]
        explicit = obj["explicit"]
        external_ids = obj["external_ids"]
        external_urls = obj["external_urls"]
        href = obj["href"]
        id = obj["id"]
        is_local = obj["is_local"]
        name = obj["name"]
        popularity = obj["popularity"]
        preview_url = obj.get("preview_url")
        track_number = obj["track_number"]
        type = obj["type"]
        uri = obj["uri"]
        return Track(
            album,
            artists,
            available_markets,
            disc_number,
            duration_ms,
            explicit,
            external_ids,
            external_urls,
            href,
            id,
            is_local,
            name,
            popularity,
            preview_url,
            track_number,
            type,
            uri,
        )

    def title_for_slack(self) -> str:
        artist_name_list = [artist["name"] for artist in self.artists]
        artist_names = ", ".join(artist_name_list)
        return f"{artist_names} - {self.name}"

    @property
    def spotify_url(self) -> str | None:
        return self.external_urls["spotify"]
