import os


class Environment:
    @staticmethod
    def is_dev():
        return os.getenv("ENVIRONMENT") == "dev"

    @staticmethod
    def is_local():
        return os.getenv("ENVIRONMENT") == "local"

    @staticmethod
    def valid_access_token(secret: str) -> None:
        if Environment.is_dev():
            return
        # SPOTIFY_CLIENT_SECRETを使って、アクセストークンを検証する
        if secret != os.getenv("SPOTIFY_CLIENT_SECRET"):
            raise Exception("invalid secret: " + secret)
