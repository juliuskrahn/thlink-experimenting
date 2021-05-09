from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, Content, ContentLocation
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy, THLINK_DOCUMENT
from app.interface import DocumentIdentifierModel, PreparedHighlightModel, DocumentModel
from app.chef import DocumentChef
from app.middleware import middleware, BadOperationUserError
from app.notification import NotificationManager


class Event(DocumentIdentifierModel, PreparedHighlightModel):
    pass


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        chef = DocumentChef(repository)
        document = chef.order(document_id, workspace)
        if LivingContentTypePolicy.is_satisfied_by(document.content.type):
            raise BadOperationUserError(f"Document content type must not be in {LivingContentTypePolicy.types}")
        highlight = document.highlight(ContentLocation(event.location), event.link_preview_text)
        if event.note_body:
            note = Content(event.note_body, THLINK_DOCUMENT)
            links = chef.prepare_links(workspace, event.links) if event.links else []
            highlight.make_note(note, links)

    response = Response.build(document)
    NotificationManager().document_mutated(response)
    return response.dict()
