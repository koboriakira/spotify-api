from typing import Optional
from usecase.authorize_usecase import AuthorizeUsecase
from infrastructure.token_info_s3_repository import TokenInfoS3Repository

repository = TokenInfoS3Repository()
authorizeUsecase = AuthorizeUsecase(repository=repository)

def get_authorize_url() -> str:
    return authorizeUsecase.get_authorize_url()

def authorize_callback(code: str) -> dict:
    return authorizeUsecase.authorize_callback(code=code)
