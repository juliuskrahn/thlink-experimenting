from typing import Union, Dict
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.parser import ValidationError
from .response_model import AppErrorResponseModel, ErrorModel
from .error import BadOperationUserError, EntityDoesNotExistUserError


def error(type_: str, message: Union[str, Dict]):
    return dict(AppErrorResponseModel(app_error=ErrorModel(type=type_, message=message)))


@lambda_handler_decorator
def middleware(handler, event, context):
    try:
        response = handler(event, context)
        return response
    except ValidationError as e:
        return error("EventValidationUserError", e.json())
    except BadOperationUserError as e:
        return error("BadOperationUserError", str(e))
    except EntityDoesNotExistUserError as e:
        return error("EntityDoesNotExistUserError", str(e))
    except:
        return error("InternalError", "Oh no!")
