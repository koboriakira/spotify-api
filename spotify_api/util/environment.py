import os

class Environment:
    @staticmethod
    def is_dev():
        return os.getenv("ENVIRONMENT") == "dev"
