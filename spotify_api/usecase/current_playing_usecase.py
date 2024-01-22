from typing import Optional
from infrastructure.spotipy import Spotipy
from domain.model.track import Track
from custom_logger import get_logger
from util.datetime import get_current_day_and_tomorrow
from domain.slack.block_builder import BlockBuilder
from service.authorization_service import AuthorizationService


logger = get_logger(__name__)

class CurrentPlayingUsecase:
    def __init__(self, authorization_service: AuthorizationService):
        access_token = authorization_service.get_access_token()
        self.spotipy = Spotipy.get_instance(access_token=access_token)

    def get_current_playing(self) -> Optional[Track]:
        return self.spotipy.get_current_playing()

    def notificate_current_playing(self) -> dict:
        track = self.get_current_playing()
        if track is None:
            return {
                "status": "info",
                "message": "no track is playing now."
            }
        self._post_to_slack(track=track)
        return {
            "status": "success",
            "message": track.title_for_slack()
        }

    def _post_to_slack(self, track: Track) -> None:
        # 面倒だし使い回さないので、このファイルに実装する
        import requests
        import json
        import os
        logger.info("post_to_slack")

        artist_name_list = [artist["name"] for artist in track.artists]

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
                        if context["artist"] == artist_name_list and context["title"] == track.name:
                            return
                    except Exception as e:
                        pass

        # Slackに投稿する
        section_text = f"<{track.spotify_url}|{track.title_for_slack()}>"
        block_builder = BlockBuilder().add_section(text=section_text)
        block_builder = block_builder.add_button_action(
            action_id="LOVE_SPOTIFY_TRACK",
            text="Love",
            value=track.id,
            style="primary")
        context = {
            "spotify_track_id": track.id,
            "artist": artist_name_list,
            "title": track.name,
        }
        block_builder = block_builder.add_context(text=context)
        blocks = block_builder.build()

        logger.info("chat.postMessage")
        url = "https://slack.com/api/chat.postMessage"
        payload = json.dumps({
            "channel": "C05HGA2TK26", # musicチャンネル
            "text": f"[Playing...] {track.title_for_slack()}",
            "blocks": blocks,
        })
        headers = {
            'Authorization': 'Bearer ' + os.environ["SLACK_BOT_TOKEN"],
            'Content-Type': 'application/json',
        }
        requests.request("POST", url, headers=headers, data=payload)
