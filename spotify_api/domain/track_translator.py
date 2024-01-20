from domain.model.track import Track


class TrackTranslator:

    @staticmethod
    def from_entity(obj: dict) -> Track:
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
        return Track(album, artists, available_markets, disc_number, duration_ms, explicit, external_ids, external_urls, href, id, is_local, name, popularity, preview_url, track_number, type, uri)
