from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import DocumentIdentifierModel, DocumentModel
from app.utils import require
from app.middleware import middleware


class Event(DocumentIdentifierModel):
    tag: str


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        document = require(repository, document_id, workspace)
        document.tag(event.tag)

    return Response.build(document).dict(by_alias=True)
