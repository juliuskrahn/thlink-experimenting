import pytest
from domain import lib
from domain.model.document.link import LinkPreview
from domain.model.document.highlight import Highlight
from tests.domain.model.document.implementations import HighlightableImplementation


@pytest.fixture
def highlight_id():
    return lib.Id()


@pytest.fixture
def parent_link_preview():
    return LinkPreview("parent", None)


@pytest.fixture
def highlight_link_preview(parent_link_preview):
    return LinkPreview("highlight", parent_link_preview)


@pytest.fixture
def highlight_parent(parent_link_preview):
    return HighlightableImplementation([], parent_link_preview)


@pytest.fixture
def highlight(highlight_id, highlight_parent, content_location, highlight_link_preview):
    return Highlight(highlight_id, highlight_parent, content_location, [])
