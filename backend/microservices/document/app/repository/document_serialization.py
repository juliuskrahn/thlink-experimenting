from typing import List, Dict
from aws_lambda_powertools.utilities.parser import BaseModel
from domain.model.document import Link, Highlight
from .document import DocumentRepositoryDocument


class SerializedLink(BaseModel):
    # key -> id: str
    location: str
    target_document_id: str
    target_document_highlight_id: str = None
    target_document_preview_text: str
    target_document_highlight_preview_text: str = None

    @classmethod
    def build(cls, link: Link):
        target_is_highlight = hasattr(link.target, "parent")
        return cls(
            location=str(link.location),
            target_document_id=str(link.target.parent.id) if target_is_highlight else str(link.target.id),
            target_document_highlight_id=str(link.target.id) if target_is_highlight else None,
            target_document_preview_text=link.target_preview.parent.text if target_is_highlight
            else link.target_preview.text,
            target_document_highlight_preview_text=link.target_preview.text if target_is_highlight else None,
        )


class SerializedBacklink(BaseModel):
    # key -> id: str
    location: str
    source_document_id: str
    source_document_highlight_id: str = None
    source_document_preview_text: str
    source_document_highlight_preview_text: str = None

    @classmethod
    def build(cls, link: Link):
        source_is_highlight = hasattr(link.source, "parent")
        return cls(
            location=str(link.location),
            source_document_id=str(link.source.parent.id) if source_is_highlight else str(link.source.id),
            source_document_highlight_id=str(link.source.id) if source_is_highlight else None,
            source_document_preview_text=link.source_preview.parent.text if source_is_highlight
            else link.source_preview.text,
            source_document_highlight_preview_text=link.source_preview.text if source_is_highlight else None,
        )


class SerializedHighlight(BaseModel):
    # key -> id: str
    location: str
    note_body: str = None
    link_preview_text: str
    links: Dict[str, SerializedLink] = None
    backlinks: Dict[str, SerializedBacklink]

    @classmethod
    def build(cls, highlight: Highlight):
        return cls(
            location=str(highlight.location),
            note_body=highlight.note.body,
            link_preview_text=highlight.link_preview.text,
            links={link.id: SerializedLink.build(link) for link in highlight.links} if highlight.links else None,
            backlinks={link.id: SerializedBacklink.build(link) for link in highlight.backlinks},
        )


class SerializedDocument(BaseModel):
    id: str
    workspace: str
    title: str
    version: int
    tags: List[str]
    content_type: str
    content_id: str
    links: Dict[str, SerializedLink]
    backlinks: Dict[str, SerializedBacklink]
    highlights: Dict[str, SerializedHighlight]
    content_id: str
    version: int
    # no need to store the link preview, because the link preview text is always the document title

    @classmethod
    def build(cls, document: DocumentRepositoryDocument):
        return cls(
            id=str(document.id),
            workspace=str(document.workspace),
            title=document.title,
            version=document.version,
            tags=document.tags,
            content_type=document.content.type,
            content_id=str(document.content_id),
            links={link.id: SerializedLink.build(link) for link in document.links},
            backlinks={link.id: SerializedBacklink.build(link) for link in document.links},
            highlights={highlight.id: SerializedHighlight.build(highlight) for highlight in document.highlights},
        )


class DocumentSerializer:

    @staticmethod
    def serialize_document(document: DocumentRepositoryDocument) -> Dict:
        return dict(SerializedDocument.build(document))
