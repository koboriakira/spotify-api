# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Spotify Web APIラッパーサービス。FastAPIベースのPython APIでSpotifyのトラック情報取得、現在再生中楽曲取得、認証を提供。AWS Lambda + API Gateway構成でデプロイされる。

## 開発コマンド

### ローカル開発
```bash
make dev  # Docker Compose起動 + ドキュメント表示（http://localhost:10120/docs）
```

### テスト実行
```bash
make cdk-test  # CDKテスト実行（cd cdk && npm run test）
```

### CDK関連
```bash
cd cdk && npm run build    # TypeScriptコンパイル
cd cdk && npm run test     # CDKテスト
cd cdk && npm run cdk      # CDK CLI
```

## アーキテクチャ

クリーンアーキテクチャベースの設計:

### レイヤー構成
- **router/**: FastAPIルーター（HTTP入出力層）
- **usecase/**: ビジネスロジック
- **service/**: サービス層（認証など）
- **infrastructure/**: 外部システム接続（Spotify API、S3など）
- **domain/**: ドメインモデル・リポジトリインターフェース
- **interface/**: アプリケーションインターフェース

### 主要エンドポイント
- `/track/{track_id}`: トラック情報取得
- `/current/playing`: 現在再生中楽曲取得
- `/authorize`: Spotify認証

### 依存関係
- Python 3.11 + pipenv
- FastAPI + Mangum（Lambda統合）
- Spotipy（Spotify Web APIクライアント）
- AWS CDK（TypeScript）でインフラ管理

### インフラ構成
- AWS Lambda（main.handler）
- API Gateway
- S3（トークン情報保存）
- EventBridge（定期実行）

## 新機能: Spotify監視システム

### 概要
24/7でSpotifyの再生履歴を監視し、S3に保存してObsidianに同期するシステム

### アーキテクチャ
1. **spotify-monitor.py** (EC2): 30秒間隔でSpotify APIを監視、S3にJSONL形式で保存
2. **sync-from-s3.py** (ローカル): S3からダウンロードしてObsidian vaultにMarkdown生成

### 主要スクリプト
- `spotify-monitor.py`: EC2用監視スクリプト
- `sync-from-s3.py`: ローカル同期スクリプト
- `setup_ec2.md`: EC2セットアップ手順

### 使用方法
```bash
# EC2での監視開始
python3 spotify-monitor.py

# ローカルでの同期実行
python sync-from-s3.py /path/to/obsidian/vault --days 7
```

## 重要な実装パターン

- 認証はヘッダ`access-token`で実行
- Token管理はS3/ローカルリポジトリの実装切り替え可能
- レスポンスオブジェクトはTranslatorパターンでドメインモデル変換
- 環境変数は`util.environment.Environment`で管理
- ログデータはJSONL形式でS3の`history/YYYY-MM-DD.jsonl`に保存