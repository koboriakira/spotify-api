import json
import boto3
from typing import Optional
from botocore.exceptions import NoCredentialsError
from domain.infrastructure.token_info_repository import TokenInfoRepository
from custom_logger import get_logger

BUCKET_NAME = "spotify-api-bucket-koboriakira"
FILE_NAME = "token_info.json"
FILE_PATH = "/tmp/" + FILE_NAME

logger = get_logger(__name__)

class TokenInfoS3Repository(TokenInfoRepository):
    def save(self, token_info: dict) -> bool:
        """
        トークン情報を保存する
        """
        # token_info.jsonを出力
        with open(FILE_PATH, 'w') as f:
            json.dump(token_info, f, indent=4)

        # S3にアップロード
        is_success = self.upload_to_s3()
        logger.info("is_success: " + str(is_success))
        return is_success

    def load(self) -> Optional[dict]:
        """
        トークン情報を取得する
        """
        # S3からダウンロード
        is_success = self.download_from_s3()
        if not is_success:
            logger.error("S3からのダウンロードに失敗しました。")
            return None

        # token_info.jsonを読み込み
        with open(FILE_PATH, 'r') as f:
            token_info = json.load(f)
        return token_info


    def upload_to_s3(self) -> bool:
        # S3クライアントを作成
        s3_client = boto3.client('s3')

        try:
            # ファイルをアップロード
            s3_client.upload_file(FILE_PATH, BUCKET_NAME, FILE_NAME)
        except FileNotFoundError:
            logger.error("ファイルが見つかりませんでした。")
            return False
        except NoCredentialsError:
            logger.error("認証情報が不足しています。")
            return False
        except Exception as e:
            logger.error(e)
            return False
        return True

    def download_from_s3(self) -> bool:
        # S3クライアントを作成
        s3_client = boto3.client('s3')

        try:
            # ファイルをダウンロード
            s3_client.download_file(BUCKET_NAME, FILE_NAME, FILE_PATH)
        except FileNotFoundError:
            logger.error("ファイルが見つかりませんでした。")
            return False
        except NoCredentialsError:
            logger.error("認証情報が不足しています。")
            return False
        except Exception as e:
            logger.error(e)
            return False
        return True

if __name__ == '__main__':
    # python -m infrastructure.token_info_s3_repository
    print(TokenInfoS3Repository().save({"access_token": "test", "refresh_token": "test"}))
