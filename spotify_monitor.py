import json
import time
import boto3
from datetime import datetime, timedelta
from typing import Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'spotify_api'))

from util.environment import Environment
from interface import track
from custom_logger import get_logger

logger = get_logger(__name__)

BUCKET_NAME = "spotify-api-bucket-koboriakira"
MONITOR_INTERVAL = 30  # 30秒間隔で監視


class HistoryLog:
    def __init__(self, track_data: dict, timestamp: datetime):
        self.track_data = track_data
        self.timestamp = timestamp
    
    def to_jsonl(self) -> str:
        return json.dumps({
            "track": self.track_data,
            "timestamp": self.timestamp.isoformat()
        })


class SpotifyMonitor:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.s3_client = boto3.client('s3')
        self.last_track_id = None
        self.current_track_start_time = None
    
    def get_current_track(self):
        """現在再生中のトラックを取得"""
        Environment.valid_access_token(self.access_token)
        return track.get_current_playing()
    
    def save_to_s3(self, jsonl_data: str, date_str: str):
        """S3にJSONLデータを保存"""
        key = f"history/{date_str}.jsonl"
        try:
            # 既存のファイルがあるかチェック
            try:
                response = self.s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                existing_data = response['Body'].read().decode('utf-8')
                jsonl_data = existing_data + jsonl_data
            except self.s3_client.exceptions.NoSuchKey:
                # ファイルが存在しない場合は新規作成
                logger.info(f"新しいファイルを作成します: {key}")
            
            self.s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=jsonl_data
            )
            logger.info(f"S3に保存しました: {key}")
        except Exception as e:
            logger.error(f"S3への保存に失敗しました: {e}")
            raise
    
    def create_track_data(self, track):
        """トラックデータをログ形式に変換"""
        return {
            "id": track.id,
            "name": track.name,
            "artists": track.artists,
            "album": track.album,
            "duration_ms": track.duration_ms,
            "external_urls": track.external_urls,
            "uri": track.uri
        }
    
    def should_log_track(self, current_track) -> bool:
        """トラックをログに記録すべきかを判定（重複防止機能含む）"""
        if current_track is None:
            return False
        
        # 新しいトラックの場合
        if self.last_track_id != current_track.id:
            self.last_track_id = current_track.id
            self.current_track_start_time = datetime.now()
            logger.info(f"新しいトラックを検出: {current_track.name}")
            return True
        
        # 同じトラックが継続して再生されている場合の重複防止
        if self.current_track_start_time:
            elapsed = datetime.now() - self.current_track_start_time
            # 最低30秒間隔でのログ記録（重複防止）
            if elapsed >= timedelta(seconds=30):
                logger.info(f"継続再生トラック記録: {current_track.name} ({elapsed.total_seconds():.1f}秒経過)")
                self.current_track_start_time = datetime.now()
                return True
        
        return False
    
    def run(self):
        """監視を開始（エラーハンドリング強化）"""
        logger.info("Spotify監視を開始します")
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                current_track = self.get_current_track()
                
                if self.should_log_track(current_track):
                    track_data = self.create_track_data(current_track)
                    timestamp = datetime.now()
                    history_log = HistoryLog(track_data, timestamp)
                    
                    # 日付ベースでファイル分割
                    date_str = timestamp.strftime("%Y-%m-%d")
                    jsonl_line = history_log.to_jsonl() + "\n"
                    
                    self.save_to_s3(jsonl_line, date_str)
                    logger.info(f"トラックをログに記録: {current_track.name} - {current_track.artists[0]['name']}")
                
                # 成功した場合はエラーカウンタをリセット
                consecutive_errors = 0
                time.sleep(MONITOR_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("監視を停止します")
                break
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"監視中にエラーが発生しました ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                # 連続エラーが多すぎる場合は長めに待機
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning(f"{max_consecutive_errors}回連続でエラーが発生しました。5分間待機します。")
                    time.sleep(300)  # 5分間待機
                    consecutive_errors = 0  # リセット
                else:
                    time.sleep(MONITOR_INTERVAL)
                    
                # 致命的エラーの場合は再起動を促す
                if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                    logger.critical("認証エラーが発生しました。アクセストークンを確認してください。")
                    break


def main():
    import os
    
    # アクセストークンを環境変数から取得
    access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if not access_token:
        logger.error("SPOTIFY_ACCESS_TOKEN環境変数が設定されていません")
        return
    
    monitor = SpotifyMonitor(access_token)
    monitor.run()


if __name__ == "__main__":
    main()