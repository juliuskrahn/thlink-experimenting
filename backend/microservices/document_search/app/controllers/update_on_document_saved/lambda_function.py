from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import DocumentSavedEventModel, EsDocumentModel
from app.es_client import get_es_client


@event_parser(model=DocumentSavedEventModel)
def handler(event: DocumentSavedEventModel, context: LambdaContext):
    # TODO get content body, if not there -> update not concerning content body
    #  -> make sure to not overwrite whole es entry
    # TODO highlight -> child
    es_client = get_es_client()
    response = es_client.index(
        index="document",
        id=event.id,
        body=EsDocumentModel(**event.dict()),
        refresh=True,
    )
