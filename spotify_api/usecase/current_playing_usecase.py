from ..custom_logger import get_logger
from ..domain.model.track import Track
from ..domain.slack.block_builder import BlockBuilder
from ..infrastructure.spotipy import Spotipy
from ..service.authorization_service import AuthorizationService
from ..util.datetime import get_current_day_and_tomorrow

logger = get_logger(__name__)

CHANNEL_ID = "C05HGA2TK26"  # musicチャンネル


class CurrentPlayingUsecase:
    def __init__(self, authorization_service: AuthorizationService):
        access_token = authorization_service.get_access_token()
        self.spotipy = Spotipy.get_instance(access_token=access_token)

    def get_current_playing(self) -> Track | None:
        return self.spotipy.get_current_playing()

    def notificate_current_playing(self) -> bool:
        track = self.get_current_playing()
        if track is None:
            logger.debug("no track is playing now.")
            return True
        self._post_to_slack(track=track)
        return True

    def _post_to_slack(self, track: Track) -> None:
        # 面倒だし使い回さないので、このファイルに実装する
        import json
        import os

        import requests

        logger.info("post_to_slack")

        # 同じ曲が投稿されているかどうかを調べる
        today, tomorrow = get_current_day_and_tomorrow()
        url = "https://slack.com/api/conversations.history"
        params = {
            "channel": CHANNEL_ID,  # musicチャンネル
            "oldest": str(today),
            "latest": str(tomorrow),
        }
        headers = {
            "Authorization": "Bearer " + os.environ["SLACK_BOT_TOKEN"],
        }
        logger.info("conversations.history")
        response = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(response.text)
        print(json.dumps(response))
        for m in response["messages"]:
            for block in m["blocks"]:
                logger.info(block)
                if block["type"] == "actions":
                    try:
                        element = block["elements"][0]
                        spotify_id = element["value"]
                        if spotify_id == track.id:
                            return
                    except Exception:
                        pass

        # Slackに投稿する
        block_builder = BlockBuilder().add_section(text=track.title_for_slack())
        block_builder = block_builder.add_button_action(
            action_id="LOVE_SPOTIFY_TRACK", text="Love", value=track.id, style="primary"
        )
        # block_builder = block_builder.add_context(text=track.id)
        blocks = block_builder.build()
        logger.info("chat.postMessage")
        url = "https://slack.com/api/chat.postMessage"
        payload = json.dumps(
            {
                "channel": CHANNEL_ID,  # musicチャンネル
                "text": track.title_for_slack(),
                "blocks": blocks,
            }
        )
        headers = {
            "Authorization": "Bearer " + os.environ["SLACK_BOT_TOKEN"],
            "Content-Type": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = response.json()
        # print(json.dumps(response_json))

        thread_ts = response_json["ts"]
        channel_id = response_json["channel"]
        payload = json.dumps(
            {
                "channel": channel_id,
                "text": track.spotify_url,
                "thread_ts": thread_ts,
            }
        )
        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = response.json()
        print(json.dumps(response_json))
