from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import DocumentDeletedEventModel
from app.es import AppDocument
from app.middleware import middleware


@middleware
@event_parser(model=DocumentDeletedEventModel)
def handler(event: DocumentDeletedEventModel, context: LambdaContext):
    s = AppDocument.search()\
        .filter("workspace", workspace=event.workspace)\
        .filter("id", workspaceid=event.document_id)
    response = s.delete()
