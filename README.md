# My Spotify API

## 使用例

ヘッダに`access-token`を指定して（SpotifyAPIのシークレット）、下記URLを呼び出す

http://localhost:10120/track/2dXME00xUY1CRcMZsM3Y4q
https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/track/2dXME00xUY1CRcMZsM3Y4q
https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/current/playing

### とくにアクセストークンの取得について

http://localhost:10120/authorize もしくは https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/authorize にアクセス

## デプロイ

GitHub Actionsのdeployワークフローを利用。

## ローカル開発

```shell
make run
```
