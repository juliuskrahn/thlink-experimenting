from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import DocumentIdentifierModel, DocumentModel
from app.chef import DocumentChef
from app.middleware import middleware
from app.notification import NotificationManager


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
        document = DocumentChef(repository).order(document_id, workspace)
        document.untag(event.tag)

        repository.on_saved_document = lambda saved_document: NotificationManager().document_saved(
            Response.build(saved_document)
        )

    response = Response.build(document)
    return response.dict()
