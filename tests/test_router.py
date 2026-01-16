"""Tests for router layer (API endpoints)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from domain.model.track import Track
from main import app
from usecase.love_track_usecase import LoveTrackResponse, LoveTrackResult


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_track(sample_track_data: dict) -> Track:
    """Create a mock Track object."""
    return Track.from_dict(sample_track_data)


class TestHealthcheck:
    """Test cases for healthcheck endpoint."""

    def test_healthcheck_returns_ok(self, client: TestClient) -> None:
        """Test that healthcheck returns ok status."""
        response = client.get("/healthcheck")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestTrackRouter:
    """Test cases for track router endpoints."""

    def test_get_track_returns_track(self, client: TestClient, mock_track: Track) -> None:
        """Test GET /track/{track_id} returns track data."""
        with patch("router.track.track.get_track") as mock_get_track:
            with patch("router.track.Environment.valid_access_token"):
                mock_get_track.return_value = mock_track

                response = client.get(
                    "/track/track123",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["data"]["id"] == "track123"
                assert data["data"]["name"] == "Test Track"

    def test_get_track_returns_error_when_not_found(self, client: TestClient) -> None:
        """Test GET /track/{track_id} returns 500 when track not found.

        Note: Current implementation returns TrackResponse(data=None) which violates
        the pydantic model constraint (data field is not optional).
        """
        with patch("router.track.track.get_track") as mock_get_track:
            with patch("router.track.Environment.valid_access_token"):
                mock_get_track.return_value = None

                response = client.get(
                    "/track/nonexistent",
                    headers={"access_token": "test_token"},
                )

                # Due to pydantic validation error, returns 500
                assert response.status_code == 500

    def test_get_track_validates_access_token(self, client: TestClient) -> None:
        """Test GET /track/{track_id} validates access token."""
        with patch("router.track.Environment.valid_access_token") as mock_validate:
            with patch("router.track.track.get_track") as mock_get_track:
                mock_get_track.return_value = None
                mock_validate.side_effect = Exception("invalid secret: wrong")

                response = client.get(
                    "/track/track123",
                    headers={"access_token": "wrong"},
                )

                assert response.status_code == 500

    def test_love_track_returns_success(self, client: TestClient) -> None:
        """Test POST /track/{track_id}/love returns success."""
        with patch("router.track.track.love_track") as mock_love:
            with patch("router.track.Environment.valid_access_token"):
                mock_love.return_value = LoveTrackResponse(result=LoveTrackResult.SUCCESS)

                response = client.post(
                    "/track/track123/love",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["data"]["result"] == "success"

    def test_love_track_returns_already_loved(self, client: TestClient) -> None:
        """Test POST /track/{track_id}/love returns already_loved."""
        with patch("router.track.track.love_track") as mock_love:
            with patch("router.track.Environment.valid_access_token"):
                mock_love.return_value = LoveTrackResponse(result=LoveTrackResult.ALREADY_LOVED)

                response = client.post(
                    "/track/track123/love",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["data"]["result"] == "already_loved"


class TestCurrentRouter:
    """Test cases for current router endpoints."""

    def test_get_current_playing_returns_track(self, client: TestClient, mock_track: Track) -> None:
        """Test GET /current/playing returns currently playing track."""
        with patch("router.current.track.get_current_playing") as mock_get:
            with patch("router.current.Environment.valid_access_token"):
                mock_get.return_value = mock_track

                response = client.get(
                    "/current/playing",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "SUCCESS"
                assert data["data"]["id"] == "track123"

    def test_get_current_playing_returns_message_when_not_playing(self, client: TestClient) -> None:
        """Test GET /current/playing returns message when nothing playing."""
        with patch("router.current.track.get_current_playing") as mock_get:
            with patch("router.current.Environment.valid_access_token"):
                mock_get.return_value = None

                response = client.get(
                    "/current/playing",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "no track is playing now."

    def test_post_current_playing_returns_success(self, client: TestClient) -> None:
        """Test POST /current/playing returns success."""
        with patch("router.current.track.post_current_playing") as mock_post:
            with patch("router.current.Environment.valid_access_token"):
                mock_post.return_value = True

                response = client.post(
                    "/current/playing",
                    headers={"access_token": "test_token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "SUCCESS"


class TestAuthorizeRouter:
    """Test cases for authorize router endpoints."""

    def test_get_authorize_redirects(self, client: TestClient) -> None:
        """Test GET /authorize redirects to Spotify."""
        with patch("router.authorize.authorize.get_authorize_url") as mock_get_url:
            mock_get_url.return_value = "https://accounts.spotify.com/authorize?test=1"

            response = client.get("/authorize", follow_redirects=False)

            assert response.status_code == 303
            assert response.headers["location"] == "https://accounts.spotify.com/authorize?test=1"

    def test_authorize_callback_returns_success(self, client: TestClient) -> None:
        """Test GET /authorize_callback returns success with code."""
        with patch("router.authorize.authorize.authorize_callback") as mock_callback:
            mock_callback.return_value = {"access_token": "test_token"}

            response = client.get("/authorize_callback?code=auth_code")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"

    def test_authorize_callback_raises_on_missing_code(self, client: TestClient) -> None:
        """Test GET /authorize_callback raises 400 when code is missing."""
        response = client.get("/authorize_callback")

        assert response.status_code == 400
        assert response.json()["detail"] == "code is not found."
