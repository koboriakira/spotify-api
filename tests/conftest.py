"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_track_data() -> dict:
    """Sample track data for testing."""
    return {
        "album": {
            "name": "Test Album",
            "id": "album123",
        },
        "artists": [
            {"name": "Test Artist", "id": "artist123"},
        ],
        "available_markets": ["JP", "US"],
        "disc_number": 1,
        "duration_ms": 180000,
        "explicit": False,
        "external_ids": {"isrc": "TEST12345678"},
        "external_urls": {"spotify": "https://open.spotify.com/track/track123"},
        "href": "https://api.spotify.com/v1/tracks/track123",
        "id": "track123",
        "is_local": False,
        "name": "Test Track",
        "popularity": 50,
        "preview_url": "https://p.scdn.co/mp3-preview/test",
        "track_number": 1,
        "type": "track",
        "uri": "spotify:track:track123",
    }
