# EC2セットアップ手順

## 1. IAM権限設定

EC2インスタンスに以下の権限が必要です：

### IAM ロール作成
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::spotify-api-bucket-koboriakira/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::spotify-api-bucket-koboriakira"
    }
  ]
}
```

## 2. 環境変数設定

EC2インスタンスで以下の環境変数を設定：

```bash
export SPOTIPY_CLIENT_ID="your_spotify_client_id"
export SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
export SPOTIPY_REDIRECT_URI="http://localhost:8080/callback"
export SPOTIFY_ACCESS_TOKEN="your_access_token"
```

## 3. パッケージインストール

```bash
# Python3とpipのインストール
sudo yum update -y
sudo yum install -y python3 python3-pip

# 必要なパッケージのインストール
pip3 install spotipy boto3 requests
```

## 4. スクリプト配置

```bash
# spotify-monitor.pyを配置
scp spotify-monitor.py ec2-user@your-instance:/home/ec2-user/
```

## 5. systemdサービス設定

`/etc/systemd/system/spotify-monitor.service`を作成：

```ini
[Unit]
Description=Spotify Monitor Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user
ExecStart=/usr/bin/python3 /home/ec2-user/spotify-monitor.py
Environment=SPOTIPY_CLIENT_ID=your_client_id
Environment=SPOTIPY_CLIENT_SECRET=your_client_secret
Environment=SPOTIPY_REDIRECT_URI=http://localhost:8080/callback
Environment=SPOTIFY_ACCESS_TOKEN=your_access_token
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 6. サービス開始

```bash
sudo systemctl daemon-reload
sudo systemctl enable spotify-monitor.service
sudo systemctl start spotify-monitor.service

# ステータス確認
sudo systemctl status spotify-monitor.service
```

## 7. ログ確認

```bash
# サービスログの確認
sudo journalctl -u spotify-monitor.service -f

# S3への保存状況確認
aws s3 ls s3://spotify-api-bucket-koboriakira/history/
```

## トラブルシューティング

### アクセストークンの更新
Spotifyアクセストークンは1時間で期限切れになるため、定期的な更新が必要です。
既存のトークン更新機能を活用して自動更新を実装してください。

### エラー対応
- **権限エラー**: IAM権限を再確認
- **ネットワークエラー**: セキュリティグループでHTTPS(443)を許可
- **S3エラー**: バケット名とリージョンを確認