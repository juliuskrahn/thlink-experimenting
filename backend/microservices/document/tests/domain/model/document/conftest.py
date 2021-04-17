import pytest
from domain.model.document.content import Content, ContentLocation


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
