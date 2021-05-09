from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, ContentLocation
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy
from app.interface import DocumentIdentifierModel, PreparedLinkModel, DocumentModel
from app.utils import require
from app.middleware import middleware, BadOperationUserError
import app.event


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
        document = require(repository, document_id, workspace)
        if LivingContentTypePolicy.is_satisfied_by(document.content.type):
            raise BadOperationUserError(f"Document content type must not be in {LivingContentTypePolicy.types}")
        document.link(
            location,
            to=require(repository, target_document_id, workspace, target_document_highlight_id),
        )

    response = Response.build(document)
    app.event.document_mutated(response)
    return response.dict(by_alias=True)
