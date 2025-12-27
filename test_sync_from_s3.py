import pytest
import json
import tempfile
import os
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
from sync_from_s3 import ObsidianSyncer, MarkdownGenerator


class TestMarkdownGenerator:
    def test_generate_for_track(self):
        track_data = {
            "id": "test_id",
            "name": "Test Song",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "external_urls": {"spotify": "https://open.spotify.com/track/test_id"}
        }
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        result = MarkdownGenerator.generate_for_track(track_data, timestamp)
        
        expected = """## Test Song - Test Artist

- **アルバム**: Test Album
- **再生時刻**: 2023-01-01 12:00:00
- **Spotify URL**: https://open.spotify.com/track/test_id

---
"""
        assert result == expected
    
    def test_generate_daily_summary(self):
        tracks = [
            {
                "track": {
                    "name": "Song 1",
                    "artists": [{"name": "Artist 1"}],
                    "album": {"name": "Album 1"},
                    "external_urls": {"spotify": "https://open.spotify.com/track/1"}
                },
                "timestamp": "2023-01-01T12:00:00"
            },
            {
                "track": {
                    "name": "Song 2", 
                    "artists": [{"name": "Artist 2"}],
                    "album": {"name": "Album 2"},
                    "external_urls": {"spotify": "https://open.spotify.com/track/2"}
                },
                "timestamp": "2023-01-01T13:00:00"
            }
        ]
        
        result = MarkdownGenerator.generate_daily_summary(tracks, date(2023, 1, 1))
        
        assert "# 2023-01-01 - 音楽リスニング履歴" in result
        assert "## Song 1 - Artist 1" in result
        assert "## Song 2 - Artist 2" in result


class TestObsidianSyncer:
    @patch('boto3.client')
    def test_download_from_s3_success(self, mock_boto3):
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        
        # S3からのレスポンスをモック
        mock_response = {
            'Body': Mock()
        }
        mock_response['Body'].read.return_value = b'{"track": {"id": "test"}, "timestamp": "2023-01-01T12:00:00"}\n'
        mock_s3.get_object.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            syncer = ObsidianSyncer(temp_dir)
            result = syncer.download_from_s3("2023-01-01")
            
            expected = [{"track": {"id": "test"}, "timestamp": "2023-01-01T12:00:00"}]
            assert result == expected
            
            mock_s3.get_object.assert_called_once_with(
                Bucket="spotify-api-bucket-koboriakira",
                Key="history/2023-01-01.jsonl"
            )
    
    @patch('boto3.client')
    def test_download_from_s3_not_found(self, mock_boto3):
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        
        # ファイルが存在しない場合をシミュレート
        mock_s3.exceptions.NoSuchKey = type('NoSuchKey', (Exception,), {})
        mock_s3.get_object.side_effect = mock_s3.exceptions.NoSuchKey()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            syncer = ObsidianSyncer(temp_dir)
            result = syncer.download_from_s3("2023-01-01")
            
            assert result == []
    
    def test_save_to_obsidian(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            syncer = ObsidianSyncer(temp_dir)
            
            tracks = [
                {
                    "track": {
                        "id": "test_id",
                        "name": "Test Song",
                        "artists": [{"name": "Test Artist"}],
                        "album": {"name": "Test Album"},
                        "external_urls": {"spotify": "https://open.spotify.com/track/test"}
                    },
                    "timestamp": "2023-01-01T12:00:00"
                }
            ]
            
            syncer.save_to_obsidian(tracks, date(2023, 1, 1))
            
            # ファイルが作成されたことを確認
            expected_path = os.path.join(temp_dir, "music", "2023-01-01.md")
            assert os.path.exists(expected_path)
            
            # ファイル内容を確認
            with open(expected_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Test Song - Test Artist" in content
    
    def test_remove_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            syncer = ObsidianSyncer(temp_dir)
            
            # 重複を含むトラックデータ
            tracks = [
                {
                    "track": {"id": "track1", "name": "Song 1", "artists": [{"name": "Artist 1"}]},
                    "timestamp": "2023-01-01T12:00:00"
                },
                {
                    "track": {"id": "track1", "name": "Song 1", "artists": [{"name": "Artist 1"}]},
                    "timestamp": "2023-01-01T12:00:30"  # 同じ分内の重複
                },
                {
                    "track": {"id": "track2", "name": "Song 2", "artists": [{"name": "Artist 2"}]},
                    "timestamp": "2023-01-01T12:01:00"
                }
            ]
            
            result = syncer.remove_duplicates(tracks)
            
            # 重複が除去されて2件になることを確認
            assert len(result) == 2
            assert result[0]["track"]["id"] == "track1"
            assert result[1]["track"]["id"] == "track2"