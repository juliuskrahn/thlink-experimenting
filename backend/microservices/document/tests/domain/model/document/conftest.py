import pytest
from domain.model.document import Document, Content, Highlight, Link, ContentLocation, Workspace


@pytest.fixture
def content():
    return Content("Lorem [[ipsum]]", "MD")


@pytest.fixture
def content_location():
    return ContentLocation("6:15")


@pytest.fixture
def workspace():
    return Workspace("MyWorkspace")


@pytest.fixture
def other_document(content, workspace):
    return Document.create(workspace, "MyOtherDocument", tags=["Other"], content=content, links=[], highlights=[])


@pytest.fixture(params=["document_with_tag", "document_with_link", "document_with_highlight"])
def document(other_document, content, content_location, request, workspace):
    other_document = other_document
    title = "MyDocument"
    tags = ["Important"] if request.param == "document_with_tag" else []
    links = [Link.prepare(content_location, other_document)] if request.param == "document_with_link" else []
    highlights = [Highlight.prepare(content_location)] if request.param == "document_with_highlight" else []
    return Document.create(workspace, title, tags, content, links, highlights)


@pytest.fixture
def highlight(document, content_location):
    # no link preview text!
    return document.highlight(content_location)


@pytest.fixture
def highlight_with_note(document, content_location, content):
    highlight = document.highlight(content_location)
    highlight.make_note(content)
    return highlight


@pytest.fixture(params=["document_link_target", "highlight_link_target"])
def link_target(request, other_document, highlight):
    if request.param == "highlight_link_target":
        return highlight
    return other_document


@pytest.fixture(params=["document_link_source", "highlight_link_source"])
def link_source(request, document, highlight):
    if request.param == "highlight_link_source":
        return highlight
    return document


@pytest.fixture
def link_from_link_source(link_source, content_location, link_target, content):
    if isinstance(link_source, Highlight):
        link = Link.prepare(content_location, link_target)
        link_source.make_note(content, [link])
        return link
    return link_source.link(content_location, link_target)
