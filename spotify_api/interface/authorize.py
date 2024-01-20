from typing import Optional
from usecase.authorize_usecase import AuthorizeUsecase

def get_authorize_url() -> str:
    authorizeUsecase = AuthorizeUsecase()
    return authorizeUsecase.get_authorize_url()

def authorize_callback(code: str) -> dict:
    authorizeUsecase = AuthorizeUsecase()
    return authorizeUsecase.authorize_callback(code=code)
