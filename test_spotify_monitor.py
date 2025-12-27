import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# 環境変数をモック
with patch.dict('os.environ', {
    'SPOTIPY_CLIENT_ID': 'test_client_id',
    'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
    'SPOTIPY_REDIRECT_URI': 'http://localhost:8080/callback',
    'ACCESS_TOKEN': 'test_access_token'
}):
    from spotify_monitor import SpotifyMonitor, HistoryLog


class TestHistoryLog:
    def test_history_log_creation(self):
        track_data = {
            "id": "test_id",
            "name": "Test Song",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "external_urls": {"spotify": "https://open.spotify.com/track/test_id"}
        }
        timestamp = datetime.now()
        
        log = HistoryLog(track_data, timestamp)
        
        assert log.track_data == track_data
        assert log.timestamp == timestamp
    
    def test_to_jsonl(self):
        track_data = {
            "id": "test_id",
            "name": "Test Song",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "external_urls": {"spotify": "https://open.spotify.com/track/test_id"}
        }
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        log = HistoryLog(track_data, timestamp)
        jsonl = log.to_jsonl()
        
        expected = {
            "track": track_data,
            "timestamp": "2023-01-01T12:00:00"
        }
        assert json.loads(jsonl) == expected


class TestSpotifyMonitor:
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8080/callback',
        'ACCESS_TOKEN': 'test_access_token'
    })
    @patch('spotify_monitor.Environment.valid_access_token')
    @patch('spotify_monitor.track.get_current_playing')
    def test_get_current_track(self, mock_get_current, mock_valid_token):
        mock_track = Mock()
        mock_track.id = "test_id"
        mock_track.name = "Test Song"
        mock_track.artists = [{"name": "Test Artist"}]
        mock_track.album = {"name": "Test Album"}
        mock_track.external_urls = {"spotify": "https://open.spotify.com/track/test_id"}
        mock_get_current.return_value = mock_track
        
        monitor = SpotifyMonitor("test_token")
        result = monitor.get_current_track()
        
        assert result == mock_track
        mock_valid_token.assert_called_once_with("test_token")
        mock_get_current.assert_called_once()
    
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8080/callback',
        'ACCESS_TOKEN': 'test_access_token'
    })
    @patch('spotify_monitor.Environment.valid_access_token')
    @patch('spotify_monitor.track.get_current_playing')
    def test_get_current_track_none(self, mock_get_current, mock_valid_token):
        mock_get_current.return_value = None
        
        monitor = SpotifyMonitor("test_token")
        result = monitor.get_current_track()
        
        assert result is None
    
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8080/callback',
        'ACCESS_TOKEN': 'test_access_token'
    })
    @patch('boto3.client')
    def test_save_to_s3_new_file(self, mock_boto3):
        """新規ファイル作成のテスト"""
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        
        # ファイルが存在しない場合をシミュレート
        mock_s3.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        mock_s3.get_object.side_effect = mock_s3.exceptions.NoSuchKey()
        
        monitor = SpotifyMonitor("test_token")
        
        # テスト用のJSONLデータ
        jsonl_data = '{"track": {"id": "test"}, "timestamp": "2023-01-01T12:00:00"}\n'
        
        monitor.save_to_s3(jsonl_data, "2023-01-01")
        
        mock_s3.put_object.assert_called_once_with(
            Bucket="spotify-api-bucket-koboriakira",
            Key="history/2023-01-01.jsonl",
            Body=jsonl_data
        )