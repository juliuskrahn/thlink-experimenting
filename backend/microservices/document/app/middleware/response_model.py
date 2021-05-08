from typing import Union, Dict
from app.interface import BaseModel


class ErrorModel(BaseModel):
    type: str
    message: Union[str, Dict]


class AppErrorResponseModel(BaseModel):
    app_error: ErrorModel = None
