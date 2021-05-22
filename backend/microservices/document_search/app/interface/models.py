from typing import List
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser.models import SnsModel


# Shared
########

class WorkspaceIdentifierModel(BaseModel):
    workspace: str


class DocumentIdentifierModel(WorkspaceIdentifierModel):
    document_id: str


# Event
#######

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


# Response
##########

class SearchResponseHighlightModel(BaseModel):
    id: str
    link_preview_text: str


class SearchResponseDocumentModel(BaseModel):
    workspace: str
    id: str
    title: str
    tags: List[str]
    highlights: List[SearchResponseHighlightModel]
    content_type: str


class SearchResponseModel(BaseModel):
    documents: List[SearchResponseDocumentModel]
