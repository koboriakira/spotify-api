import json
from typing import Optional
from domain.infrastructure.token_info_repository import TokenInfoRepository
from custom_logger import get_logger

FILE_NAME = "token_info.json"
FILE_PATH = "/tmp/" + FILE_NAME

logger = get_logger(__name__)


class TokenInfoLocalRepository(TokenInfoRepository):
    def save(self, token_info: dict) -> bool:
        """
        トークン情報を保存する
        """
        # token_info.jsonを出力
        with open(FILE_PATH, 'w') as f:
            json.dump(token_info, f, indent=4)
        return True

    def load(self) -> Optional[dict]:
        """
        トークン情報を取得する
        """
        # token_info.jsonを読み込み
        with open(FILE_PATH, 'r') as f:
            token_info = json.load(f)
        return token_info

if __name__ == '__main__':
    # python -m infrastructure.token_info_local_repository
    print(TokenInfoLocalRepository().save({"access_token": "test", "refresh_token": "test"}))
    print(TokenInfoLocalRepository().load())
