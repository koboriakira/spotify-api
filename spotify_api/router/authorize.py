from fastapi import APIRouter, Header, Response, Request, HTTPException
from interface import authorize
from router.response import BaseResponse
from custom_logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/authorize", status_code=303)
def get_authorize():
    """ Spotifyの認証ページにリダイレクト """
    authorize_url = authorize.get_authorize_url()
    return Response(headers={"Location": authorize_url}, status_code=303)

@router.get("/authorize_callback", response_model=BaseResponse)
async def authorize_callback(request: Request):
    """
    Spotifyの認証後のコールバック用URL。
    get_authorize() -> Spotifyの認証画面 -> authorize_callback()とリダイレクトされる。
    """
    code = request.query_params.get('code')
    if code is None:
        raise HTTPException(status_code=400, detail="code is not found.")
    result = authorize.authorize_callback(code=code)
    logger.debug(result)
    return BaseResponse()
