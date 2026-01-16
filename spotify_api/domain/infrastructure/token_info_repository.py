from abc import ABCMeta, abstractmethod
from typing import Any


class TokenInfoRepository(metaclass=ABCMeta):
    """
    Spotifyのトークン情報を管理する
    """

    @abstractmethod
    def save(self, token_info: dict[str, Any]) -> bool:
        """
        トークン情報を保存する
        """
        pass

    @abstractmethod
    def load(self) -> dict[str, Any] | None:
        """
        トークン情報を取得する
        """
        pass
