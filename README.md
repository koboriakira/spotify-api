# My Spotify API

Spotify Web APIのラッパーAPIサービス。FastAPIで構築され、AWS Lambdaにデプロイ可能。

## 機能

- **トラック取得**: Spotify track IDを指定してトラック情報を取得
- **現在再生中の取得**: 現在再生中のトラック情報を取得
- **いいね機能**: 指定したトラックを「いいね」に追加
- **Slack通知**: 現在再生中のトラックをSlackに通知
- **OAuth認証**: Spotify OAuth 2.0認証フロー

## 技術スタック

- **言語**: Python 3.11
- **フレームワーク**: FastAPI
- **Spotify連携**: spotipy
- **インフラ**: AWS Lambda + API Gateway (CDKでデプロイ)
- **開発環境**: Docker Compose

## 環境変数

`.env.template`を参考に`.env`ファイルを作成:

```
ENVIRONMENT=dev          # dev または prod
SPOTIFY_CLIENT_ID=       # Spotify Developer DashboardのClient ID
SPOTIFY_CLIENT_SECRET=   # Spotify Developer DashboardのClient Secret
SLACK_BOT_TOKEN=         # Slack Bot Token（Slack通知機能用）
```

## ローカル開発

```shell
# Docker Composeで起動
make dev

# ブラウザでSwagger UIが開く
# http://localhost:10120/docs
```

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/healthcheck` | ヘルスチェック |
| GET | `/authorize` | Spotify認証ページへリダイレクト |
| GET | `/authorize_callback` | OAuth認証コールバック |
| GET | `/track/{track_id}` | 指定トラックの情報を取得 |
| POST | `/track/{track_id}/love` | 指定トラックを「いいね」に追加 |
| GET | `/current/playing` | 現在再生中のトラックを取得 |
| POST | `/current/playing` | 現在再生中のトラックをSlackに通知 |

### 認証

APIリクエストには`access-token`ヘッダが必要です。

### アクセストークンの取得

1. `/authorize` エンドポイントにアクセス
2. Spotifyの認証画面で認可
3. コールバックでトークンが保存される

## デプロイ

GitHub Actionsの`deploy`ワークフローを利用（mainブランチへのpushで自動デプロイ）。

手動でCDKデプロイする場合:
```shell
cd cdk
npm install
npx cdk deploy
```

## プロジェクト構成

```
spotify_api/
├── main.py                 # FastAPIアプリケーションのエントリーポイント
├── router/                 # APIルーター
│   ├── track.py           # トラック関連エンドポイント
│   ├── current.py         # 現在再生中関連エンドポイント
│   ├── authorize.py       # 認証関連エンドポイント
│   └── response/          # レスポンスモデル
├── interface/              # インターフェース層
├── usecase/               # ユースケース層
├── domain/                # ドメイン層
│   └── model/            # ドメインモデル
└── infrastructure/        # インフラ層（Spotify API連携、リポジトリ）

cdk/                       # AWS CDKインフラコード
docker/                    # Dockerファイル
```
