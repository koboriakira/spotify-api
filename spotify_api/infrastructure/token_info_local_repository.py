import json
from typing import Any, cast

from ..custom_logger import get_logger
from ..domain.infrastructure.token_info_repository import TokenInfoRepository

FILE_NAME = "token_info.json"
FILE_PATH = "/tmp/" + FILE_NAME

logger = get_logger(__name__)


class TokenInfoLocalRepository(TokenInfoRepository):
    def save(self, token_info: dict[str, Any]) -> bool:
        """
        トークン情報を保存する
        """
        # token_info.jsonを出力
        with open(FILE_PATH, "w") as f:
            json.dump(token_info, f, indent=4)
        return True

    def load(self) -> dict[str, Any] | None:
        """
        トークン情報を取得する
        """
        # token_info.jsonを読み込み
        try:
            with open(FILE_PATH) as f:
                token_info = json.load(f)
            return cast(dict[str, Any], token_info)
        except FileNotFoundError:
            logger.warning(f"Token file not found: {FILE_PATH}")
            return None


if __name__ == "__main__":
    # python -m infrastructure.token_info_local_repository
    print(TokenInfoLocalRepository().save({"access_token": "test", "refresh_token": "test"}))
    print(TokenInfoLocalRepository().load())
