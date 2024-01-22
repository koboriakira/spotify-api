import json
import boto3
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
        is_success = self.upload_to_s3(FILE_PATH)
        logger.info("is_success: " + str(is_success))
        return is_success


    def upload_to_s3(self, file_name: str) -> bool:
        """
        ファイルをS3バケットにアップロードする関数
        :param file_name: アップロードするファイルのパス
        :param object_name: S3バケット内のファイル名。Noneの場合はfile_nameが使用される
        :return: ファイルのアップロードが成功した場合はTrueを返し、そうでない場合はFalseを返す

        使用例
        upload_to_s3('example.txt', 'my-s3-bucket')
        """
        # S3クライアントを作成
        s3_client = boto3.client('s3')

        try:
            # ファイルをアップロード
            s3_client.upload_file(file_name, BUCKET_NAME, file_name)
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
