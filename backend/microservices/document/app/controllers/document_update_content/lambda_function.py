from typing import Any, List
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, Content
from app.repository import DocumentRepository, DocumentContentUpdatedByOtherUserError
from app.implementation import LivingContentTypePolicy
from app.interface import DocumentIdentifierModel, PreparedLinkModel, DocumentModel
from app.utils import require, prepare_links
from app.middleware import middleware, BadOperationUserError


class Event(DocumentIdentifierModel):
    content_body: Any
    links: List[PreparedLinkModel] = None


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    try:

        with DocumentRepository.use() as repository:
            document = require(repository, document_id, workspace)
            if not LivingContentTypePolicy.is_satisfied_by(document.content.type):
                raise BadOperationUserError(f"Document content type must be in {LivingContentTypePolicy.types}")
            content = Content(event.content_body, document.content.type)
            links = prepare_links(repository, workspace, event.links) if event.links else []
            document.update_content(content, links, highlights=[])

        return Response.build(document, with_content_body=True).dict(by_alias=True)

    except DocumentContentUpdatedByOtherUserError:
        raise BadOperationUserError("Document content updated by other user")
