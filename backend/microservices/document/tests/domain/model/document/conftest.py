import pytest
from domain.model.document.content import Content, ContentLocation
from domain.model.document.link import LinkPreview
from domain.model.document.highlight import Highlight
from tests.domain.model.document.implementations import HighlightableImplementation


@pytest.fixture
def content_body():
    return "# content body"


@pytest.fixture
def content_type():
    return "md"


@pytest.fixture
def content(content_body, content_type):
    return Content(content_body, content_type)


@pytest.fixture
def content_location():
    return ContentLocation("1:2")


@pytest.fixture
def link_preview():
    return LinkPreview("preview", None)


@pytest.fixture
def child_link_preview(link_preview):
    return LinkPreview("child", link_preview)


@pytest.fixture
def highlight_parent(link_preview):
    return HighlightableImplementation([], link_preview)


@pytest.fixture
def highlight_child(highlight_parent, content_location):
    return Highlight.create(highlight_parent, content_location)


@pytest.fixture
def highlight_child_with_content(highlight_parent, content_location, content):
    highlight = Highlight.create(highlight_parent, content_location)
    highlight.content = content
    return highlight
