# Claude Development Guide

このドキュメントはAI（Claude）がこのプロジェクトで効率的に作業するためのコンテキストを提供します。

## プロジェクト概要

Spotify Web APIのラッパーAPIサービス。FastAPI + Python 3.11で構築され、AWS Lambda上で稼働。

## アーキテクチャ

クリーンアーキテクチャに基づいた4層構造:

```
router/        → プレゼンテーション層（APIエンドポイント定義）
interface/     → インターフェース層（ルーターとユースケースの橋渡し）
usecase/       → ユースケース層（ビジネスロジック）
domain/        → ドメイン層（モデル、リポジトリインターフェース）
infrastructure/→ インフラ層（外部サービス連携、リポジトリ実装）
```

## 主要ファイル

- `spotify_api/main.py` - FastAPIアプリケーションのエントリーポイント
- `spotify_api/router/track.py` - トラック関連APIエンドポイント
- `spotify_api/router/current.py` - 現在再生中関連APIエンドポイント
- `spotify_api/router/authorize.py` - OAuth認証関連エンドポイント
- `spotify_api/infrastructure/spotipy.py` - Spotify API連携（spotipyラッパー）
- `spotify_api/domain/model/track.py` - Trackドメインモデル

## 開発コマンド

```shell
# ローカル開発環境起動
make dev

# CDKテスト
make cdk-test
```

## コーディング規約

- Pythonコードはpipenvで管理
- 型ヒントを使用
- ドメインモデルは`@dataclass(frozen=True)`でイミュータブルに
- レスポンスモデルはPydanticを使用
- 環境変数は`util/environment.py`で管理

## テスト

- CDKのテストは`cdk/test/`にある
- Pythonのテストは未実装

## デプロイ

GitHub Actionsの`deploy`ワークフロー（`.github/workflows/deploy.yml`）がmainブランチへのpushで自動実行。

## 環境変数

| 変数名 | 説明 |
|--------|------|
| ENVIRONMENT | dev または prod |
| SPOTIFY_CLIENT_ID | Spotify API Client ID |
| SPOTIFY_CLIENT_SECRET | Spotify API Client Secret |
| SLACK_BOT_TOKEN | Slack通知用Bot Token |

## API認証

すべてのAPIエンドポイント（`/authorize`と`/authorize_callback`を除く）は`access-token`ヘッダによる認証が必要。

## 依存関係

主要パッケージ:
- fastapi==0.99.0
- pydantic==1.10.9
- mangum==0.17.0 (AWS Lambda対応)
- spotipy (Spotify Web API)
- boto3 (AWS SDK)

## 注意事項

- トークン情報はローカル開発時はファイル、本番環境ではS3に保存
- Slack通知機能は`SLACK_BOT_TOKEN`が設定されている場合のみ動作
