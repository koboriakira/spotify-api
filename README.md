# My Spotify API

## 使用例

ヘッダに`access-token`を指定して（SpotifyAPIのシークレット）、下記URLを呼び出す

https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1

### とくにアクセストークンの取得について

http://localhost:10120/authorize もしくは https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/authorize にアクセス

## デプロイ

GitHub Actionsのdeployワークフローを利用。

## ローカル開発

```shell
make run
```
