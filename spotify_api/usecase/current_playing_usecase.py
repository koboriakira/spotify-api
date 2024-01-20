from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track
from custom_logger import get_logger
from util.datetime import get_current_day_and_tomorrow

logger = get_logger(__name__)

class CurrentPlayingUsecase:
    def __init__(self):
        self.spotipy = Spotipy.get_instance()

    def get_current_playing(self) -> Optional[Track]:
        return self.spotipy.get_current_playing()

    def notificate_current_playing(self) -> None:
        track = self.get_current_playing()
        if track is None:
            return
        self._post_to_slack(track=track)

    def _post_to_slack(self, track: Track) -> None:
        # 面倒だし使い回さないので、このファイルに実装する
        import requests
        import json
        import os
        logger.info("post_to_slack")

        # 同じ曲が投稿されているかどうかを調べる
        today, tomorrow = get_current_day_and_tomorrow()
        url = "https://slack.com/api/conversations.history"
        params = {
            "channel": "C05HGA2TK26", # musicチャンネル
            "oldest": str(today),
            "latest": str(tomorrow),
        }
        headers = {
            'Authorization': 'Bearer ' + os.environ["SLACK_BOT_TOKEN"],
        }
        logger.info("conversations.history")
        response = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(response.text)
        for m in response["messages"]:
            for block in m["blocks"]:
                logger.info(block)
                if block["type"] == "context":
                    try:
                        context = json.loads(block["elements"][0]["text"])
                        if context["artist"] == track.artists and context["title"] == track.name:
                            return
                    except Exception as e:
                        pass

        # Slackに投稿する
        logger.info("chat.postMessage")
        url = "https://slack.com/api/chat.postMessage"
        payload = json.dumps({
            "channel": "C05HGA2TK26", # musicチャンネル
            "text": f"[Playing...] {track.title_for_slack()}"
        })
        headers = {
            'Authorization': 'Bearer ' + os.environ["SLACK_BOT_TOKEN"],
            'Content-Type': 'application/json',
        }
        requests.request("POST", url, headers=headers, data=payload)
