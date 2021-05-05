from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import DocumentIdentifierModel


class Event(DocumentIdentifierModel):
    pass


class Response(DocumentIdentifierModel):
    pass


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        document = repository.get(document_id, workspace)
        document.delete()

    return dict(Response(document_id=document.id, workspace=document.workspace))
