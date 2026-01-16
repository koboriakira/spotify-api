from abc import ABCMeta, abstractmethod


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
    def load(self) -> dict | None:
        """
        トークン情報を取得する
        """
        pass
