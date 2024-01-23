from pydantic import Field
from router.response.base_response import BaseResponse

class AuthorizeResponse(BaseResponse):
    data: dict = Field(description="Authorize data")
