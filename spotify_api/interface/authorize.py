from typing import Optional
from usecase.authorize_usecase import AuthorizeUsecase
from infrastructure.token_info_s3_repository import TokenInfoS3Repository
from infrastructure.token_info_local_repository import TokenInfoLocalRepository
from util.environment import Environment

repository = TokenInfoS3Repository() if not Environment.is_dev() else TokenInfoLocalRepository()
authorizeUsecase = AuthorizeUsecase(repository=repository)

def get_authorize_url() -> str:
    return authorizeUsecase.get_authorize_url()

def authorize_callback(code: str) -> dict:
    return authorizeUsecase.authorize_callback(code=code)
