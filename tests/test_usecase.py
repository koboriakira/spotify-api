"""Tests for usecase layer."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from domain.model.track import Track
from usecase.authorize_usecase import AuthorizeUsecase
from usecase.get_track_usecase import GetTrackUsecase
from usecase.love_track_usecase import LoveTrackResponse, LoveTrackResult, LoveTrackUsecase


class TestGetTrackUsecase:
    """Test cases for GetTrackUsecase."""

    def test_execute_returns_track(self, sample_track_data: dict) -> None:
        """Test that execute returns a Track when found."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_access_token.return_value = "test_access_token"

        mock_track = Track.from_dict(sample_track_data)

        with patch("usecase.get_track_usecase.Spotipy") as mock_spotipy_class:
            mock_spotipy = MagicMock()
            mock_spotipy.get_track.return_value = mock_track
            mock_spotipy_class.get_instance.return_value = mock_spotipy

            usecase = GetTrackUsecase(authorization_service=mock_auth_service)
            result = usecase.execute(track_id="track123")

            assert result is not None
            assert result.id == "track123"
            assert result.name == "Test Track"
            mock_spotipy.get_track.assert_called_once_with("track123")

    def test_execute_returns_none_when_not_found(self) -> None:
        """Test that execute returns None when track not found."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_access_token.return_value = "test_access_token"

        with patch("usecase.get_track_usecase.Spotipy") as mock_spotipy_class:
            mock_spotipy = MagicMock()
            mock_spotipy.get_track.return_value = None
            mock_spotipy_class.get_instance.return_value = mock_spotipy

            usecase = GetTrackUsecase(authorization_service=mock_auth_service)
            result = usecase.execute(track_id="nonexistent")

            assert result is None


class TestLoveTrackUsecase:
    """Test cases for LoveTrackUsecase."""

    def test_execute_success_when_not_saved(self) -> None:
        """Test that love_track succeeds when track is not already saved."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_access_token.return_value = "test_access_token"

        with patch("usecase.love_track_usecase.Spotipy") as mock_spotipy_class:
            mock_spotipy = MagicMock()
            mock_spotipy.is_track_saved.return_value = False
            mock_spotipy_class.get_instance.return_value = mock_spotipy

            usecase = LoveTrackUsecase(authorization_service=mock_auth_service)
            result = usecase.execute(track_id="track123")

            assert isinstance(result, LoveTrackResponse)
            assert result.result == LoveTrackResult.SUCCESS
            mock_spotipy.love_track.assert_called_once_with("track123")

    def test_execute_already_loved_when_saved(self) -> None:
        """Test that love_track returns already_loved when track is saved."""
        mock_auth_service = MagicMock()
        mock_auth_service.get_access_token.return_value = "test_access_token"

        with patch("usecase.love_track_usecase.Spotipy") as mock_spotipy_class:
            mock_spotipy = MagicMock()
            mock_spotipy.is_track_saved.return_value = True
            mock_spotipy_class.get_instance.return_value = mock_spotipy

            usecase = LoveTrackUsecase(authorization_service=mock_auth_service)
            result = usecase.execute(track_id="track123")

            assert isinstance(result, LoveTrackResponse)
            assert result.result == LoveTrackResult.ALREADY_LOVED
            mock_spotipy.love_track.assert_not_called()


class TestLoveTrackResponse:
    """Test cases for LoveTrackResponse."""

    def test_love_track_response_is_frozen(self) -> None:
        """Test that LoveTrackResponse is immutable."""
        from dataclasses import FrozenInstanceError

        response = LoveTrackResponse(result=LoveTrackResult.SUCCESS)

        with pytest.raises(FrozenInstanceError):
            response.result = LoveTrackResult.FAILED


class TestAuthorizeUsecase:
    """Test cases for AuthorizeUsecase."""

    def test_get_authorize_url(self) -> None:
        """Test get_authorize_url returns the URL from SpotifyOauth."""
        mock_repository = MagicMock()

        with patch("usecase.authorize_usecase.SpotifyOauth") as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth.get_authorize_url.return_value = "https://accounts.spotify.com/authorize?test"
            mock_oauth_class.return_value = mock_oauth

            usecase = AuthorizeUsecase(repository=mock_repository)
            result = usecase.get_authorize_url()

            assert result == "https://accounts.spotify.com/authorize?test"
            mock_oauth.get_authorize_url.assert_called_once()

    def test_authorize_callback_saves_token(self) -> None:
        """Test authorize_callback saves token and returns it."""
        mock_repository = MagicMock()
        mock_token_info = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": 9999999999,
        }

        with patch("usecase.authorize_usecase.SpotifyOauth") as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth.authorize_callback.return_value = mock_token_info
            mock_oauth_class.return_value = mock_oauth

            usecase = AuthorizeUsecase(repository=mock_repository)
            result = usecase.authorize_callback(code="auth_code")

            assert result == mock_token_info
            mock_oauth.authorize_callback.assert_called_once_with(code="auth_code")
            mock_repository.save.assert_called_once_with(token_info=mock_token_info)
