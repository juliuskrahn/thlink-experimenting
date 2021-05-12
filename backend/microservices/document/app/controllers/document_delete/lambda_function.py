from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository, DocumentRepositoryDocument
from app.interface import DocumentIdentifierModel
from app.middleware import middleware
from app.notification import NotificationManager


class Event(DocumentIdentifierModel):
    pass


class Response(DocumentIdentifierModel):

    @classmethod
    def build(cls, document: DocumentRepositoryDocument):
        return cls(documentId=str(document.id), workspace=str(document.workspace))


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        document = repository.get(document_id, workspace)
        if document:
            document.delete()

        repository.on_deleted_document = lambda deleted_document: NotificationManager().document_deleted(
            Response.build(deleted_document)
        )

    response = Response.build(document)
    return response.dict()
