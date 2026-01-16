"""Tests for infrastructure layer."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from domain.model.track import Track
from domain.track_translator import TrackTranslator
from infrastructure.spotipy import Spotipy
from infrastructure.token_info_local_repository import TokenInfoLocalRepository
from infrastructure.token_info_s3_repository import TokenInfoS3Repository


class TestTokenInfoLocalRepository:
    """Test cases for TokenInfoLocalRepository."""

    def test_save_writes_to_file(self) -> None:
        """Test that save writes token info to file."""
        token_info = {"access_token": "test_token", "refresh_token": "refresh"}
        m = mock_open()

        with patch("builtins.open", m):
            repo = TokenInfoLocalRepository()
            result = repo.save(token_info)

            assert result is True
            m.assert_called_once_with("/tmp/token_info.json", "w")

    def test_load_reads_from_file(self) -> None:
        """Test that load reads token info from file."""
        token_info = {"access_token": "test_token", "refresh_token": "refresh"}
        m = mock_open(read_data=json.dumps(token_info))

        with patch("builtins.open", m):
            repo = TokenInfoLocalRepository()
            result = repo.load()

            assert result == token_info
            m.assert_called_once_with("/tmp/token_info.json")


class TestTokenInfoS3Repository:
    """Test cases for TokenInfoS3Repository."""

    def test_save_uploads_to_s3(self) -> None:
        """Test that save uploads token info to S3."""
        token_info = {"access_token": "test_token", "refresh_token": "refresh"}
        m = mock_open()

        with patch("builtins.open", m):
            with patch("boto3.client") as mock_boto:
                mock_s3 = MagicMock()
                mock_boto.return_value = mock_s3

                repo = TokenInfoS3Repository()
                result = repo.save(token_info)

                assert result is True
                mock_s3.upload_file.assert_called_once()

    def test_save_returns_false_on_upload_error(self) -> None:
        """Test that save returns False when S3 upload fails."""
        token_info = {"access_token": "test_token"}
        m = mock_open()

        with patch("builtins.open", m):
            with patch("boto3.client") as mock_boto:
                mock_s3 = MagicMock()
                mock_s3.upload_file.side_effect = Exception("Upload failed")
                mock_boto.return_value = mock_s3

                repo = TokenInfoS3Repository()
                result = repo.save(token_info)

                assert result is False

    def test_load_downloads_from_s3(self) -> None:
        """Test that load downloads token info from S3."""
        token_info = {"access_token": "test_token", "refresh_token": "refresh"}
        m = mock_open(read_data=json.dumps(token_info))

        with patch("builtins.open", m):
            with patch("boto3.client") as mock_boto:
                mock_s3 = MagicMock()
                mock_boto.return_value = mock_s3

                repo = TokenInfoS3Repository()
                result = repo.load()

                assert result == token_info
                mock_s3.download_file.assert_called_once()

    def test_load_returns_none_on_download_error(self) -> None:
        """Test that load returns None when S3 download fails."""
        with patch("boto3.client") as mock_boto:
            mock_s3 = MagicMock()
            mock_s3.download_file.side_effect = Exception("Download failed")
            mock_boto.return_value = mock_s3

            repo = TokenInfoS3Repository()
            result = repo.load()

            assert result is None

    def test_upload_to_s3_handles_file_not_found(self) -> None:
        """Test that upload_to_s3 handles FileNotFoundError."""
        with patch("boto3.client") as mock_boto:
            mock_s3 = MagicMock()
            mock_s3.upload_file.side_effect = FileNotFoundError()
            mock_boto.return_value = mock_s3

            repo = TokenInfoS3Repository()
            result = repo.upload_to_s3()

            assert result is False

    def test_download_from_s3_handles_file_not_found(self) -> None:
        """Test that download_from_s3 handles FileNotFoundError."""
        with patch("boto3.client") as mock_boto:
            mock_s3 = MagicMock()
            mock_s3.download_file.side_effect = FileNotFoundError()
            mock_boto.return_value = mock_s3

            repo = TokenInfoS3Repository()
            result = repo.download_from_s3()

            assert result is False


class TestSpotipy:
    """Test cases for Spotipy wrapper."""

    def test_get_instance_creates_spotipy_client(self) -> None:
        """Test that get_instance creates a Spotipy instance."""
        with patch("infrastructure.spotipy.spotipy.Spotify") as mock_spotify_class:
            mock_spotify = MagicMock()
            mock_spotify_class.return_value = mock_spotify

            instance = Spotipy.get_instance(access_token="test_token")

            mock_spotify_class.assert_called_once_with(auth="test_token")
            assert instance.sp == mock_spotify

    def test_get_track_returns_track(self, sample_track_data: dict) -> None:
        """Test that get_track returns a Track object."""
        mock_sp = MagicMock()
        mock_sp.track.return_value = sample_track_data

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.get_track(track_id="track123")

        assert result is not None
        assert isinstance(result, Track)
        assert result.id == "track123"
        mock_sp.track.assert_called_once_with(track_id="track123")

    def test_get_track_returns_none_when_not_found(self) -> None:
        """Test that get_track returns None when track not found."""
        mock_sp = MagicMock()
        mock_sp.track.return_value = None

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.get_track(track_id="nonexistent")

        assert result is None

    def test_get_current_playing_returns_track(self, sample_track_data: dict) -> None:
        """Test that get_current_playing returns currently playing track."""
        mock_sp = MagicMock()
        mock_sp.current_user_playing_track.return_value = {"item": sample_track_data}

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.get_current_playing()

        assert result is not None
        assert isinstance(result, Track)
        assert result.id == "track123"

    def test_get_current_playing_returns_none_when_nothing_playing(self) -> None:
        """Test that get_current_playing returns None when nothing is playing."""
        mock_sp = MagicMock()
        mock_sp.current_user_playing_track.return_value = None

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.get_current_playing()

        assert result is None

    def test_love_track_calls_api(self) -> None:
        """Test that love_track calls the Spotify API."""
        mock_sp = MagicMock()

        spotipy = Spotipy(sp=mock_sp)
        spotipy.love_track(track_id="track123")

        mock_sp.current_user_saved_tracks_add.assert_called_once_with(tracks=["track123"])

    def test_is_track_saved_returns_true_when_saved(self) -> None:
        """Test that is_track_saved returns True when track is saved."""
        mock_sp = MagicMock()
        mock_sp.current_user_saved_tracks_contains.return_value = [True]

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.is_track_saved(track_id="track123")

        assert result is True
        mock_sp.current_user_saved_tracks_contains.assert_called_once_with(tracks=["track123"])

    def test_is_track_saved_returns_false_when_not_saved(self) -> None:
        """Test that is_track_saved returns False when track is not saved."""
        mock_sp = MagicMock()
        mock_sp.current_user_saved_tracks_contains.return_value = [False]

        spotipy = Spotipy(sp=mock_sp)
        result = spotipy.is_track_saved(track_id="track123")

        assert result is False

    def test_current_user_recently_played_not_implemented(self) -> None:
        """Test that current_user_recently_played raises NotImplementedError."""
        mock_sp = MagicMock()
        spotipy = Spotipy(sp=mock_sp)

        with pytest.raises(NotImplementedError):
            spotipy.current_user_recently_played()

    def test_get_album_not_implemented(self) -> None:
        """Test that get_album raises NotImplementedError."""
        mock_sp = MagicMock()
        spotipy = Spotipy(sp=mock_sp)

        with pytest.raises(NotImplementedError):
            spotipy.get_album(album_id="album123")


class TestTrackTranslator:
    """Test cases for TrackTranslator."""

    def test_from_entity_creates_track(self, sample_track_data: dict) -> None:
        """Test that from_entity creates a Track from dict."""
        track = TrackTranslator.from_entity(sample_track_data)

        assert track.id == "track123"
        assert track.name == "Test Track"
        assert track.duration_ms == 180000

    def test_from_entity_handles_missing_preview_url(self, sample_track_data: dict) -> None:
        """Test that from_entity handles missing preview_url."""
        del sample_track_data["preview_url"]
        track = TrackTranslator.from_entity(sample_track_data)

        assert track.preview_url is None
