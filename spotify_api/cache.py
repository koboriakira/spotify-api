from typing import Optional
import datetime

class Cache(object):
    __token_info: Optional[dict] = None

    @staticmethod
    def write_token_info(token_info: dict):
        Cache.__token_info = token_info

    @staticmethod
    def get_access_token() -> str|bool:
        """
        アクセストークンを返す。
        期限切れの場合はFalseを返す。
        """
        if Cache.__token_info is None:
            raise Exception("cache is empty.")
        if Cache.__token_info["expires_at"] < datetime.datetime.now().timestamp():
            return False
        return Cache.__token_info["access_token"]


    @staticmethod
    def get_refresh_token() -> str:
        """
        リフレッシュトークンを返す。
        """
        if Cache.__token_info == {}:
            raise Exception("cache is empty.")
        return Cache.__token_info["refresh_token"]
