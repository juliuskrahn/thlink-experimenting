from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace, Content
from app.repository import DocumentRepository
from app.implementation import THLINK_DOCUMENT
from app.interface import DocumentHighlightIdentifierModel, HighlightMakeNoteModel, DocumentModel
from app.utils import require, prepare_links
from app.middleware import middleware


class Event(DocumentHighlightIdentifierModel, HighlightMakeNoteModel):
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
        document = repository.get(document_id, workspace)
        highlight = require(repository, document_id, workspace, document_highlight_id)
        if event.note_body:
            note = Content(event.note_body, THLINK_DOCUMENT)
            links = prepare_links(repository, workspace, event.links) if event.links else []
            highlight.make_note(note, links)
        else:
            highlight.delete_note()

    return dict(Response.build(document))
