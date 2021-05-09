from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy
from app.interface import SourceDocumentLinkIdentifierModel, DocumentModel
from app.chef import DocumentChef
from app.middleware import middleware, BadOperationUserError
from app.notification import NotificationManager


class Event(SourceDocumentLinkIdentifierModel):
    pass


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)
    document_link_id = lib.Id(event.document_link_id)

    with DocumentRepository.use() as repository:
        document = DocumentChef(repository).order(document_id, workspace)
        if LivingContentTypePolicy.is_satisfied_by(document.content.type):
            raise BadOperationUserError(f"Document content type must not be in {LivingContentTypePolicy.types}")
        link = document.get_link(document_link_id)
        if link:
            link.delete()

    response = Response.build(document)
    NotificationManager().document_mutated(response)
    return response.dict()
