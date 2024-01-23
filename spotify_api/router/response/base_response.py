from pydantic import BaseModel, Field
from typing import Any

class BaseResponse(BaseModel):
    # SUCCESS, WARNING, ERRORのどれか
    status: str = Field(default="SUCCESS")
    message: str = Field(default="")
    data: Any = Field(default=None)

    def __init__(self, status: str = "SUCCESS", message: str = "", data: Any = None):
        super().__init__(status=status, message=message, data=data)
