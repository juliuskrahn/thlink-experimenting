import pytest
from domain.model.document import Document, Content, Highlight, Link, ContentLocation


@pytest.fixture
def content():
    return Content("Lorem [[ipsum]]", "MD")


@pytest.fixture
def content_location():
    return ContentLocation("6:15")


@pytest.fixture
def other_document(content):
    return Document.create("MyOtherDocument", tags=["Other"], content=content, links=[], highlights=[])


@pytest.fixture(params=["document_with_tag", "document_with_link", "document_with_highlight"])
def document(other_document, content, content_location, request):
    other_document = other_document
    title = "MyDocument"
    tags = ["Important"] if request.param == "document_with_tag" else []
    links = [Link.prepare(content_location, other_document)] if request.param == "document_with_link" else []
    highlights = [Highlight.prepare(content_location)] if request.param == "document_with_highlight" else []
    return Document.create(title, tags, content, links, highlights)
