import pytest
from domain.model.document.link import LinkPreview


@pytest.fixture
def parent_link_preview():
    return LinkPreview("parent", None)


@pytest.fixture
def child_link_preview(parent_link_preview):
    return LinkPreview("child", parent_link_preview)


def test_parent_link_preview_init(parent_link_preview):
    assert parent_link_preview.text == "parent"
    assert parent_link_preview.parent is None


def test_child_link_preview_init(child_link_preview, parent_link_preview):
    assert child_link_preview.text == "child"
    assert child_link_preview.parent == parent_link_preview
