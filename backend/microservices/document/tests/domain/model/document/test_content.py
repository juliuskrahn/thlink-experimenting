import pytest
from domain.model.document.content import ContentLocatable


@pytest.fixture
def content_locatable(content_location):
    return ContentLocatable(content_location)


def test_content(content, content_body, content_type):
    assert content.body == content_body
    assert content.type == content_type


def test_content_locatable(content_locatable, content_location):
    assert content_locatable.location == content_location
