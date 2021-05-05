from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.parser import ValidationError
from .error import BadOperationUserError, EntityDoesNotExistUserError


@lambda_handler_decorator
def middleware(handler, event, context):
    try:
        response = handler(event, context)
        return response
    except ValidationError as e:
        return {
            "appError": {
                "type": "EventValidationUserError",
                "message": e.json(),
            },
        }
    except BadOperationUserError as e:
        return {
            "appError": {
                "type": "BadOperationUserError",
                "message": e,
            },
        }
    except EntityDoesNotExistUserError as e:
        return {
            "appError": {
                "type": "EntityDoesNotExistUserError",
                "message": e,
            },
        }
    except:
        return {
            "appError": {
                "type": "InternalError",
                "message": "Oh no!",
            },
        }
