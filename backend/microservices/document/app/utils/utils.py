from typing import List
from domain import lib
from domain.model.document import Link, Workspace, ContentLocation
from app.repository import DocumentRepository
from app.interface import PreparedLinkModel
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
        target_document_highlight_id = lib.Id(link_model.target_document_highlight_id)\
            if link_model.target_document_highlight_id else None
        prepared_links.append(Link.prepare(
            location=ContentLocation(link_model.location),
            target=require(repository, target_document_id, workspace, target_document_highlight_id)
        ))
    return prepared_links
