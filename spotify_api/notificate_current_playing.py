import json
import os
import requests
from interface import track
from cache import Cache


def error() -> dict:
    url = "https://slack.com/api/chat.postMessage"
    payload = json.dumps({
        "channel": "C04Q3AV4TA5", # 通知チャンネル
        "text": f"Spotifyの認証が必要です。 https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/authorize",
    })
    headers = {
        'Authorization': 'Bearer ' + os.environ["SLACK_BOT_TOKEN"],
        'Content-Type': 'application/json',
    }
    requests.request("POST", url, headers=headers, data=payload)
    return {
        "message": "Spotifyの認証が必要です",
    }


def handler(event, context):
    try:
        if Cache.get_access_token():
            return track.post_current_playing()
        else:
            return error()
    except Exception as e:
        return error()


if __name__ == "__main__":
    # python -m notificate_current_playing
    print(handler({}, {}))
