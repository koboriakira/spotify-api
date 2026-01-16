"""Tests for utility functions."""

import os
import sys
from datetime import datetime as DatetimeObject
from pathlib import Path
from unittest.mock import patch

import pytest

# Add spotify_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "spotify_api"))

from util.datetime import get_current_day_and_tomorrow
from util.environment import Environment


class TestGetCurrentDayAndTomorrow:
    """Test cases for get_current_day_and_tomorrow function."""

    def test_with_specific_date(self) -> None:
        """Test with a specific date string."""
        today, tomorrow = get_current_day_and_tomorrow("2024-01-15")

        # 2024-01-15 00:00:00 in Unix timestamp (local time)
        expected_today = DatetimeObject(2024, 1, 15).timestamp()
        expected_tomorrow = expected_today + 86400

        assert today == expected_today
        assert tomorrow == expected_tomorrow

    def test_tomorrow_is_24_hours_later(self) -> None:
        """Test that tomorrow is exactly 24 hours after today."""
        today, tomorrow = get_current_day_and_tomorrow("2024-06-01")

        assert tomorrow - today == 86400  # 24 hours in seconds

    def test_with_none_uses_current_date(self) -> None:
        """Test that None date parameter uses current date."""
        with patch("util.datetime.DatetimeObject") as mock_datetime:
            mock_now = DatetimeObject(2024, 3, 20, 14, 30, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strptime = DatetimeObject.strptime
            mock_datetime.side_effect = lambda *args, **kwargs: DatetimeObject(*args, **kwargs)

            today, tomorrow = get_current_day_and_tomorrow(None)

            # Should be called with "2024-03-20"
            expected_today = DatetimeObject(2024, 3, 20).timestamp()
            expected_tomorrow = expected_today + 86400

            assert today == expected_today
            assert tomorrow == expected_tomorrow

    def test_leap_year_date(self) -> None:
        """Test with a leap year date."""
        today, tomorrow = get_current_day_and_tomorrow("2024-02-29")

        expected_today = DatetimeObject(2024, 2, 29).timestamp()
        expected_tomorrow = expected_today + 86400

        assert today == expected_today
        assert tomorrow == expected_tomorrow

    def test_year_boundary(self) -> None:
        """Test date at year boundary."""
        today, tomorrow = get_current_day_and_tomorrow("2024-12-31")

        expected_today = DatetimeObject(2024, 12, 31).timestamp()
        expected_tomorrow = expected_today + 86400

        assert today == expected_today
        assert tomorrow == expected_tomorrow


class TestEnvironment:
    """Test cases for Environment class."""

    def test_is_dev_returns_true_when_dev(self) -> None:
        """Test is_dev returns True when ENVIRONMENT is dev."""
        with patch.dict(os.environ, {"ENVIRONMENT": "dev"}):
            assert Environment.is_dev() is True

    def test_is_dev_returns_false_when_not_dev(self) -> None:
        """Test is_dev returns False when ENVIRONMENT is not dev."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            assert Environment.is_dev() is False

    def test_is_dev_returns_false_when_unset(self) -> None:
        """Test is_dev returns False when ENVIRONMENT is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove ENVIRONMENT if it exists
            os.environ.pop("ENVIRONMENT", None)
            assert Environment.is_dev() is False

    def test_is_local_returns_true_when_local(self) -> None:
        """Test is_local returns True when ENVIRONMENT is local."""
        with patch.dict(os.environ, {"ENVIRONMENT": "local"}):
            assert Environment.is_local() is True

    def test_is_local_returns_false_when_not_local(self) -> None:
        """Test is_local returns False when ENVIRONMENT is not local."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            assert Environment.is_local() is False

    def test_valid_access_token_passes_in_dev(self) -> None:
        """Test valid_access_token does not raise in dev mode."""
        with patch.dict(os.environ, {"ENVIRONMENT": "dev"}):
            # Should not raise any exception
            Environment.valid_access_token("any_secret")

    def test_valid_access_token_passes_with_correct_secret(self) -> None:
        """Test valid_access_token passes with correct secret."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SPOTIFY_CLIENT_SECRET": "correct_secret"}):
            # Should not raise any exception
            Environment.valid_access_token("correct_secret")

    def test_valid_access_token_raises_with_wrong_secret(self) -> None:
        """Test valid_access_token raises with incorrect secret."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SPOTIFY_CLIENT_SECRET": "correct_secret"}):
            with pytest.raises(Exception) as exc_info:
                Environment.valid_access_token("wrong_secret")

            assert "invalid secret" in str(exc_info.value)
