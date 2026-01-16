"""Tests for service layer."""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from service.authorization_service import AuthorizationService


class TestAuthorizationService:
    """Test cases for AuthorizationService."""

    def test_get_access_token_returns_token_when_valid(self) -> None:
        """Test that get_access_token returns token when not expired."""
        mock_repository = MagicMock()
        future_timestamp = datetime.now().timestamp() + 3600  # 1 hour in future
        mock_repository.load.return_value = {
            "access_token": "valid_token",
            "refresh_token": "refresh_token",
            "expires_at": future_timestamp,
        }

        with patch("service.authorization_service.SpotifyOauth"):
            service = AuthorizationService(token_repository=mock_repository)
            result = service.get_access_token()

            assert result == "valid_token"
            mock_repository.load.assert_called_once()

    def test_get_access_token_refreshes_when_expired(self) -> None:
        """Test that get_access_token refreshes token when expired."""
        mock_repository = MagicMock()
        past_timestamp = datetime.now().timestamp() - 3600  # 1 hour in past
        mock_repository.load.return_value = {
            "access_token": "old_token",
            "refresh_token": "refresh_token",
            "expires_at": past_timestamp,
        }

        new_token_info = {
            "access_token": "new_token",
            "refresh_token": "new_refresh_token",
            "expires_at": datetime.now().timestamp() + 3600,
        }

        with patch("service.authorization_service.SpotifyOauth") as mock_oauth_class:
            mock_oauth = MagicMock()
            mock_oauth.refresh_access_token.return_value = new_token_info
            mock_oauth_class.return_value = mock_oauth

            service = AuthorizationService(token_repository=mock_repository)
            result = service.get_access_token()

            assert result == "new_token"
            mock_oauth.refresh_access_token.assert_called_once_with("refresh_token")
            mock_repository.save.assert_called_once_with(token_info=new_token_info)

    def test_get_access_token_raises_when_no_token(self) -> None:
        """Test that get_access_token raises exception when no token exists."""
        mock_repository = MagicMock()
        mock_repository.load.return_value = None

        with patch("service.authorization_service.SpotifyOauth"):
            service = AuthorizationService(token_repository=mock_repository)

            with pytest.raises(Exception) as exc_info:
                service.get_access_token()

            assert "token_info is not found" in str(exc_info.value)
