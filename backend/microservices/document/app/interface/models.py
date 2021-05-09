from typing import Any, List
from domain.model.document import Link, Highlight
from app.repository import DocumentRepositoryDocument
from .base_model import BaseModel


# TODO remove redundant attrs ~> None?


class PreparedLinkModel(BaseModel):
    location: str
    target_document_id: str
    target_document_highlight_id: str = None


class LinkModel(PreparedLinkModel):
    id: str
    target_document_preview_text: str
    target_document_highlight_preview_text: str = None

    @classmethod
    def build(cls, link: Link):
        target_is_highlight = hasattr(link.target, "parent")
        return cls(
            id=str(link.id),
            location=str(link.location),
            targetDocumentId=str(link.target.parent.id) if target_is_highlight else str(link.target.id),
            targetDocumentDighlightId=str(link.target.id) if target_is_highlight else None,
            targetDocumentPreviewText=link.target_preview.parent.text if target_is_highlight
            else link.target_preview.text,
            targetDocumentHighlightPreviewText=link.target_preview.text if target_is_highlight else None,
        )


class BacklinkModel(BaseModel):
    location: str
    id: str
    source_document_id: str
    source_document_highlight_id: str = None
    source_document_preview_text: str
    source_document_highlight_preview_text: str = None

    @classmethod
    def build(cls, link: Link):
        source_is_highlight = hasattr(link.source, "parent")
        return cls(
            id=str(link.id),
            location=str(link.location),
            sourceDocumentId=str(link.source.parent.id) if source_is_highlight else str(link.source.id),
            sourceDocumentHighlightId=str(link.source.id) if source_is_highlight else None,
            sourceDocumentPreviewText=link.source_preview.parent.text if source_is_highlight
            else link.source_preview.text,
            sourceDocumentHighlightPreviewText=link.source_preview.text if source_is_highlight else None,
        )


class HighlightMakeNoteModel(BaseModel):
    note_body: str = None
    links: List[PreparedLinkModel] = None
    link_preview_text: str


class PreparedHighlightModel(HighlightMakeNoteModel):
    location: str


class HighlightModel(PreparedHighlightModel):
    id: str
    links: List[LinkModel] = None
    backlinks: List[BacklinkModel]

    @classmethod
    def build(cls, highlight: Highlight):
        return cls(
            id=str(highlight.id),
            location=str(highlight.location),
            noteBody=highlight.note.body if highlight.note else None,
            linkPreviewText=highlight.link_preview.text,
            links=[LinkModel.build(link) for link in highlight.links] if highlight.links else None,
            backlinks=[BacklinkModel.build(link) for link in highlight.backlinks],
        )


class PreparedDocumentModel(BaseModel):
    workspace: str
    title: str
    tags: List[str]
    content_type: str
    content_body: Any
    links: List[PreparedLinkModel] = None


class DocumentModel(BaseModel):
    id: str
    workspace: str
    title: str
    tags: List[str]
    content_type: str
    content_body_url: str
    links: List[LinkModel]
    backlinks: List[BacklinkModel]
    highlights: List[HighlightModel]

    @classmethod
    def build(cls, document: DocumentRepositoryDocument, with_content_body_url=False):
        return cls(
            id=str(document.id),
            workspace=str(document.workspace),
            title=document.title,
            tags=document.tags,
            contentType=document.content.type,
            contentBodyUrl=document.content_body_url if with_content_body_url else None,
            links=[LinkModel.build(link) for link in document.links],
            backlinks=[BacklinkModel.build(link) for link in document.backlinks],
            highlights=[HighlightModel.build(highlight) for highlight in document.highlights],
        )


class WorkspaceIdentifierModel(BaseModel):
    workspace: str


class DocumentIdentifierModel(WorkspaceIdentifierModel):
    document_id: str


class DocumentHighlightIdentifierModel(DocumentIdentifierModel):
    document_highlight_id: str


class SourceDocumentLinkIdentifierModel(DocumentIdentifierModel):
    document_link_id: str
