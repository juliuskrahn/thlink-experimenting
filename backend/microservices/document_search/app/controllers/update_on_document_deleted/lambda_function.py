from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import DocumentDeletedEventModel
from app.es_client import get_es_client


@event_parser(model=DocumentDeletedEventModel)
def handler(event: DocumentDeletedEventModel, context: LambdaContext):
    es_client = get_es_client()
    response = es_client.delete(
        index="document",
        id=event.document_id,
        refresh=True,
    )
