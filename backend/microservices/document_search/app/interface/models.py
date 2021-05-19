from typing import List
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser.models import SnsModel


class WorkspaceIdentifierModel(BaseModel):
    workspace: str


class DocumentIdentifierModel(WorkspaceIdentifierModel):
    document_id: str


class LinkModel(BaseModel):
    pass


class HighlightModel(BaseModel):
    id: str
    link_preview_text: str
    links: List[LinkModel] = None
    backlinks: List[LinkModel]


class DocumentSavedEventModel(SnsModel):
    id: str
    workspace: str
    title: str
    tags: List[str]
    content_type: str
    content_body_url: str = None
    links: List[LinkModel]
    backlinks: List[LinkModel]
    highlights: List[HighlightModel]


class DocumentDeletedEventModel(SnsModel, DocumentIdentifierModel):
    pass


class SearchEventModel(WorkspaceIdentifierModel):
    query: str
    include_highlights = False
