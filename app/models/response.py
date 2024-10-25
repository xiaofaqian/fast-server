from typing import Any
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class ResponseModel(BaseModel):
    code: int
    msg: str
    data: Any = None

    class Config:
        arbitrary_types_allowed = True

def custom_http_exception_handler(exc: HTTPException):
    response_model = ResponseModel(code=exc.status_code, msg=exc.detail, data=None)
    return JSONResponse(status_code=exc.status_code, content=response_model.model_dump())