# Spotify リスニングヒストリー監視システム

GitHub Issue #1 の対応として、24/7でSpotifyの再生履歴を自動監視し、ObsidianにMarkdown形式で同期するシステムを実装しました。

## 機能概要

1. **監視システム** (`spotify-monitor.py`): EC2上で24時間365日Spotify再生状況を監視
2. **同期システム** (`sync-from-s3.py`): S3に保存されたログをローカルPCのObsidianに同期

## アーキテクチャ

```
スマートフォン → Spotify API → EC2(monitoring) → S3 → ローカルPC → Obsidian
```

### データフロー
1. スマートフォンで音楽再生
2. EC2インスタンスがSpotify APIを30秒間隔で監視
3. 再生情報をS3にJSONL形式で日別保存
4. ローカルPCが起動時にS3から最新データを取得
5. Obsidian vault内にMarkdownファイルとして保存

## ファイル構成

- `spotify-monitor.py`: EC2用監視スクリプト
- `sync-from-s3.py`: ローカル同期スクリプト
- `setup_ec2.md`: EC2セットアップ手順
- `test_spotify_monitor.py`: 監視システムのテスト
- `test_sync_from_s3.py`: 同期システムのテスト

## セットアップ

### 1. EC2での監視開始

```bash
# 環境変数設定
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret" 
export SPOTIPY_REDIRECT_URI="http://localhost:8080/callback"
export SPOTIFY_ACCESS_TOKEN="your_access_token"

# 監視開始
python3 spotify-monitor.py
```

### 2. ローカルでの同期実行

```bash
# 最近7日間を同期
python sync-from-s3.py /path/to/obsidian/vault --days 7

# 特定期間を同期
python sync-from-s3.py /path/to/obsidian/vault --start-date 2023-01-01 --end-date 2023-01-07

# 既存ファイルを上書き
python sync-from-s3.py /path/to/obsidian/vault --days 7 --overwrite
```

## 主要機能

### 重複防止
- 同一トラック・同一分内の記録は自動的に重複除去
- 最低30秒間隔での記録で無駄なログを削減

### エラーハンドリング
- 一時的なネットワークエラーに対する自動リトライ
- 連続エラー時の待機時間自動調整
- 認証エラー時の適切な通知

### ログ形式
S3保存形式（JSONL）:
```json
{"track": {"id": "track_id", "name": "曲名", "artists": [{"name": "アーティスト名"}], "album": {"name": "アルバム名"}, "external_urls": {"spotify": "https://..."}}, "timestamp": "2023-01-01T12:00:00"}
```

Obsidian出力形式（Markdown）:
```markdown
# 2023-01-01 - 音楽リスニング履歴

## 曲名 - アーティスト名

- **アルバム**: アルバム名
- **再生時刻**: 2023-01-01 12:00:00
- **Spotify URL**: https://open.spotify.com/track/...
```

## テスト実行

```bash
# 全テスト実行
pipenv run python -m pytest test_spotify_monitor.py test_sync_from_s3.py -v

# 個別テスト
pipenv run python -m pytest test_spotify_monitor.py -v
pipenv run python -m pytest test_sync_from_s3.py -v
```

## 設定ファイル

詳細な設定手順は以下を参照:
- `setup_ec2.md`: EC2セットアップとsystemdサービス設定
- `CLAUDE.md`: プロジェクト全体の設定と使用方法

## 注意事項

1. **アクセストークンの期限**: Spotifyアクセストークンは1時間で期限切れ
2. **IAM権限**: EC2にS3への読み書き権限が必要
3. **ネットワーク**: EC2からSpotify API (HTTPS/443) への接続が必要