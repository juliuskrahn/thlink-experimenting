from typing import Union, Dict
import logging
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import ValidationError
from .response_model import AppErrorResponseModel, ErrorModel


logger = Logger(service="Document", level=logging.INFO)


def error(type_: str, message: Union[str, Dict]):
    return dict(AppErrorResponseModel(app_error=ErrorModel(type=type_, message=message)))


@lambda_handler_decorator
def middleware(handler, event, context):
    logger.inject_lambda_context(log_event=logger.level == logging.DEBUG)(handler)
    try:
        response = handler(event, context)
        logger.debug("Handler Response", extra=response)
        return response
    except ValidationError as e:
        logger.info("EventValidationUserError")
        return error("EventValidationUserError", e.json())
    except:
        logger.exception("InternalError")
        return error("InternalError", "Oh no!")
