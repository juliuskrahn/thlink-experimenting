from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, ContentLocation
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy
from app.interface import DocumentIdentifierModel, PreparedLinkModel, DocumentModel
from app.chef import DocumentChef
from app.middleware import middleware, BadOperationUserError
from app.notification import NotificationManager


class Event(DocumentIdentifierModel, PreparedLinkModel):
    pass


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)
    location = ContentLocation(event.location)
    target_document_id = lib.Id(event.target_document_id)
    target_document_highlight_id = lib.Id(event.target_document_highlight_id)\
        if event.target_document_highlight_id else None

    with DocumentRepository.use() as repository:
        chef = DocumentChef(repository)
        document = chef.order(document_id, workspace)
        if LivingContentTypePolicy.is_satisfied_by(document.content.type):
            raise BadOperationUserError(f"Document content type must not be in {LivingContentTypePolicy.types}")
        document.link(
            location,
            to=chef.order(target_document_id, workspace, target_document_highlight_id),
        )

    response = Response.build(document)
    NotificationManager().document_mutated(response)
    return response.dict()
