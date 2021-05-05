from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, Content, Link, ContentLocation
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy, THLINK_DOCUMENT
from app.interface import DocumentIdentifierModel, PreparedHighlightModel, DocumentModel
from app.utils import prepare_links


class Event(DocumentIdentifierModel, PreparedHighlightModel):
    pass


class Response(DocumentModel):
    pass


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        document = repository.get(document_id, workspace)
        assert not LivingContentTypePolicy.is_satisfied_by(document.content.type)
        highlight = document.highlight(ContentLocation(event.location), event.link_preview_text)
        if event.note_body:
            note = Content(event.note_body, THLINK_DOCUMENT)
            links = prepare_links(repository, workspace, event.links) if event.links else []
            highlight.make_note(note, links)

    return dict(Response.build(document))
