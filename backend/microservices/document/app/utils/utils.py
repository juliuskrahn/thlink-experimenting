from typing import List
from domain import lib
from domain.model.document import Link, Workspace, ContentLocation, Highlight, Content
from app.repository import DocumentRepository
from app.implementation import THLINK_DOCUMENT
from app.interface import PreparedLinkModel, PreparedHighlightModel
from app.middleware import EntityDoesNotExistUserError


def require(repository: DocumentRepository, document_id: lib.Id, workspace: Workspace,
            document_highlight_id: lib.Id = None):
    document = repository.get(document_id, workspace)
    if not document:
        raise EntityDoesNotExistUserError(f"Document(id='{document_id}', workspace='{workspace}') does not exist")
    if document_highlight_id:
        highlight = document.get_highlight(document_highlight_id)
        if not highlight:
            raise EntityDoesNotExistUserError(f"Highlight(id='{document_highlight_id}') does not exist on "
                                              f"Document(id='{document_id}', workspace='{workspace}')")
        return highlight
    return document


def prepare_links(repository: DocumentRepository, workspace: Workspace, link_models: List[PreparedLinkModel]):
    prepared_links = []
    for link_model in link_models:
        target_document_id = lib.Id(link_model.target_document_id)
        target_document_highlight_id = lib.Id(link_model.target_document_highlight_id)
        prepared_links.append(Link.prepare(
            location=ContentLocation(link_model.location),
            target=require(repository, target_document_id, workspace, target_document_highlight_id)
        ))
    return prepared_links


def prepare_highlights(repository: DocumentRepository, workspace: Workspace,
                       highlight_models: List[PreparedHighlightModel]):
    prepared_highlights = []
    for highlight_model in highlight_models:
        prepared_highlight = Highlight.prepare(
            location=ContentLocation(highlight_model.location),
            link_preview_text=highlight_model.link_preview_text,
        )
        if highlight_model.note_body:
            prepared_highlight.make_note(
                note=Content(highlight_model.note_body, THLINK_DOCUMENT),
                links=prepare_links(repository, workspace, highlight_model.links)
            )
        prepared_highlights.append(prepared_highlight)
    return prepared_highlights
