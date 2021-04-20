from domain.model.document.content import Content, ContentLocation, ContentLocatable


def test_content():
    content = Content("Lorem [[ipsum]]", "MD")
    assert content.body == "Lorem [[ipsum]]"
    assert content.type == "MD"


def test_content_locatable():
    content_locatable = ContentLocatable(ContentLocation("6:15"))
    assert content_locatable.location == "6:15"
