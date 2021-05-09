from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import DocumentHighlightIdentifierModel, DocumentModel
from app.utils import require
from app.middleware import middleware
import app.event


class Event(DocumentHighlightIdentifierModel):
    pass


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)
    document_highlight_id = lib.Id(event.document_highlight_id)

    with DocumentRepository.use() as repository:
        document = require(repository, document_id, workspace)
        highlight = document.get_highlight(document_highlight_id)
        if highlight:
            highlight.delete()

    response = Response.build(document)
    app.event.document_mutated(response)
    return response.dict(by_alias=True)
