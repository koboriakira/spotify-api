import json
import os
import boto3
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = "spotify-api-bucket-koboriakira"


class MarkdownGenerator:
    @staticmethod
    def generate_for_track(track_data: Dict[str, Any], timestamp: datetime) -> str:
        """1つのトラックに対するMarkdownを生成"""
        artist_names = ", ".join([artist["name"] for artist in track_data["artists"]])
        album_name = track_data["album"]["name"]
        spotify_url = track_data["external_urls"]["spotify"]
        
        return f"""## {track_data["name"]} - {artist_names}

- **アルバム**: {album_name}
- **再生時刻**: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}
- **Spotify URL**: {spotify_url}

---
"""
    
    @staticmethod
    def generate_daily_summary(tracks: List[Dict[str, Any]], target_date: date) -> str:
        """1日分の全トラックのMarkdownサマリーを生成"""
        header = f"# {target_date.strftime('%Y-%m-%d')} - 音楽リスニング履歴\n\n"
        header += f"合計再生回数: {len(tracks)}曲\n\n"
        
        content = header
        
        for track_entry in tracks:
            track_data = track_entry["track"]
            timestamp = datetime.fromisoformat(track_entry["timestamp"])
            content += MarkdownGenerator.generate_for_track(track_data, timestamp)
        
        return content


class ObsidianSyncer:
    def __init__(self, obsidian_vault_path: str):
        self.obsidian_vault_path = obsidian_vault_path
        self.s3_client = boto3.client('s3')
        self.music_folder = os.path.join(obsidian_vault_path, "music")
        
        # musicフォルダが存在しない場合は作成
        os.makedirs(self.music_folder, exist_ok=True)
    
    def download_from_s3(self, date_str: str) -> List[Dict[str, Any]]:
        """S3から指定日のJSONLファイルをダウンロードして解析"""
        key = f"history/{date_str}.jsonl"
        
        try:
            response = self.s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            # JSONLを行ごとに解析
            tracks = []
            for line in content.strip().split('\n'):
                if line:
                    tracks.append(json.loads(line))
            
            logger.info(f"S3から{len(tracks)}件のトラック情報を取得しました: {date_str}")
            return tracks
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f"S3にファイルが見つかりません: {key}")
            return []
        except Exception as e:
            logger.error(f"S3からのダウンロードエラー: {e}")
            raise
    
    def save_to_obsidian(self, tracks: List[Dict[str, Any]], target_date: date):
        """トラック情報をObsidian形式のMarkdownファイルとして保存（重複除去付き）"""
        if not tracks:
            logger.info(f"保存するトラック情報がありません: {target_date}")
            return
        
        # 重複除去（同一トラックID + 同一時刻の除去）
        unique_tracks = self.remove_duplicates(tracks)
        logger.info(f"重複除去: {len(tracks)}件 -> {len(unique_tracks)}件")
        
        # Markdownコンテンツ生成
        markdown_content = MarkdownGenerator.generate_daily_summary(unique_tracks, target_date)
        
        # ファイルパス生成
        filename = f"{target_date.strftime('%Y-%m-%d')}.md"
        file_path = os.path.join(self.music_folder, filename)
        
        # ファイル保存
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Obsidianファイルを保存しました: {file_path}")
    
    def remove_duplicates(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複するトラック記録を除去"""
        seen = set()
        unique_tracks = []
        
        for track_entry in tracks:
            # トラックIDとタイムスタンプの分（秒以下は無視）で重複判定
            track_id = track_entry["track"]["id"]
            timestamp_str = track_entry["timestamp"]
            timestamp_minute = timestamp_str[:16]  # YYYY-MM-DDTHH:MM部分のみ
            
            key = (track_id, timestamp_minute)
            
            if key not in seen:
                seen.add(key)
                unique_tracks.append(track_entry)
            else:
                logger.debug(f"重複を除去: {track_entry['track']['name']} at {timestamp_str}")
        
        return unique_tracks
    
    def check_existing_files(self) -> List[date]:
        """既存のObsidianファイルの日付リストを取得"""
        existing_dates = []
        
        if not os.path.exists(self.music_folder):
            return existing_dates
        
        for filename in os.listdir(self.music_folder):
            if filename.endswith('.md') and len(filename) == 13:  # YYYY-MM-DD.md
                try:
                    date_str = filename[:-3]  # .mdを除去
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    existing_dates.append(file_date)
                except ValueError:
                    continue
        
        return sorted(existing_dates)
    
    def sync_date_range(self, start_date: date, end_date: date, overwrite: bool = False):
        """指定された日付範囲を同期"""
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            file_path = os.path.join(self.music_folder, f"{date_str}.md")
            
            # 既存ファイルがある場合の処理
            if os.path.exists(file_path) and not overwrite:
                logger.info(f"ファイルが既に存在します（スキップ）: {date_str}")
                current_date += timedelta(days=1)
                continue
            
            # S3からダウンロード
            tracks = self.download_from_s3(date_str)
            
            # Obsidianに保存
            if tracks:
                self.save_to_obsidian(tracks, current_date)
            
            current_date += timedelta(days=1)
    
    def sync_recent_days(self, days: int = 7, overwrite: bool = False):
        """最近の指定日数を同期"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        logger.info(f"最近{days}日間を同期します: {start_date} 〜 {end_date}")
        self.sync_date_range(start_date, end_date, overwrite)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Spotify履歴をS3からObsidianに同期')
    parser.add_argument('vault_path', help='Obsidian vaultのパス')
    parser.add_argument('--days', type=int, default=7, help='同期する日数（デフォルト: 7日）')
    parser.add_argument('--start-date', help='開始日（YYYY-MM-DD形式）')
    parser.add_argument('--end-date', help='終了日（YYYY-MM-DD形式）')
    parser.add_argument('--overwrite', action='store_true', help='既存ファイルを上書き')
    
    args = parser.parse_args()
    
    syncer = ObsidianSyncer(args.vault_path)
    
    if args.start_date and args.end_date:
        # 日付範囲指定での同期
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        syncer.sync_date_range(start_date, end_date, args.overwrite)
    else:
        # 最近の日数での同期
        syncer.sync_recent_days(args.days, args.overwrite)


if __name__ == "__main__":
    main()