from abc import ABCMeta, abstractmethod
from typing import Optional

class TokenInfoRepository(metaclass=ABCMeta):
    """
    Spotifyのトークン情報を管理する
    """

    @abstractmethod
    def save(self, token_info: dict) -> bool:
        """
        トークン情報を保存する
        """
        pass

    @abstractmethod
    def load(self) -> Optional[dict]:
        """
        トークン情報を取得する
        """
        pass
