from typing import Optional
import datetime

class Cache(object):
    __token_info: Optional[dict] = None

    @staticmethod
    def write_token_info(token_info: dict):
        Cache.__token_info = token_info

    @staticmethod
    def get_access_token() -> str:
        if Cache.__token_info == {}:
            raise Exception("cache is empty.")
        if Cache.__token_info["expires_at"] < datetime.datetime.now().timestamp():
            # logger.info("access_token is expired.")
            # FIXME: ここでrefresh_tokenを使って、access_tokenを更新する
            raise Exception("access_token is expired.")
        return Cache.__token_info["access_token"]
