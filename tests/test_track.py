"""Tests for the Track domain model."""

import sys
from pathlib import Path

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from domain.model.track import Track


class TestTrack:
    """Test cases for Track model."""

    def test_from_dict(self, sample_track_data: dict) -> None:
        """Test creating Track from dictionary."""
        track = Track.from_dict(sample_track_data)

        assert track.id == "track123"
        assert track.name == "Test Track"
        assert track.duration_ms == 180000
        assert track.explicit is False
        assert track.popularity == 50

    def test_title_for_slack(self, sample_track_data: dict) -> None:
        """Test Slack title formatting."""
        track = Track.from_dict(sample_track_data)

        title = track.title_for_slack()

        assert title == "Test Artist - Test Track"

    def test_title_for_slack_multiple_artists(self, sample_track_data: dict) -> None:
        """Test Slack title with multiple artists."""
        sample_track_data["artists"] = [
            {"name": "Artist One", "id": "artist1"},
            {"name": "Artist Two", "id": "artist2"},
        ]
        track = Track.from_dict(sample_track_data)

        title = track.title_for_slack()

        assert title == "Artist One, Artist Two - Test Track"

    def test_spotify_url(self, sample_track_data: dict) -> None:
        """Test Spotify URL property."""
        track = Track.from_dict(sample_track_data)

        assert track.spotify_url == "https://open.spotify.com/track/track123"

    def test_preview_url_optional(self, sample_track_data: dict) -> None:
        """Test that preview_url can be None."""
        sample_track_data["preview_url"] = None
        track = Track.from_dict(sample_track_data)

        assert track.preview_url is None

    def test_track_is_frozen(self, sample_track_data: dict) -> None:
        """Test that Track is immutable (frozen dataclass)."""
        from dataclasses import FrozenInstanceError

        import pytest

        track = Track.from_dict(sample_track_data)

        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            track.name = "Modified Name"
