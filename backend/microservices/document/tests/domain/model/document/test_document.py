from domain.model.document import Document, Content, Highlight, Link


def test_can_create_document_with_title(content):
    document = Document.create("MyDocument", tags=[], content=content, links=[], highlights=[])
    assert document.title == "MyDocument"


def test_can_change_document_title(document):
    document.title = "MyModifiedDocument"
    assert document.title == "MyModifiedDocument"


def test_can_create_document_with_tags(content):
    document = Document.create("MyDocument", tags=["Important"], content=content, links=[], highlights=[])
    assert document.tags == ["Important"]


def test_can_add_tag_to_document(document):
    document.tag("New")
    assert "New" in document.tags


def test_can_remove_tag_from_document(document):
    document.tag("New")
    document.untag("New")
    assert "New" not in document.tags


def test_can_create_document_with_content():
    content = Content("Lorem", "MD")
    document = Document.create("MyDocument", tags=[], content=content,  links=[], highlights=[])
    assert document.content == content


def test_can_create_document_with_highlights(content, content_location):
    highlight = Highlight.prepare(content_location)
    document = Document.create("MyDocument", tags=[], content=content, links=[],
                               highlights=[highlight])
    assert highlight in document.highlights
    assert document.get_highlight(highlight.id) is highlight


def test_can_create_document_with_links(content, content_location, link_target):
    link = Link.prepare(content_location, link_target)
    document = Document.create("MyDocument", tags=[], content=content,
                               links=[link],
                               highlights=[])
    assert link in document.links
    assert document.get_link(link.id) is link


def test_can_update_document_content_and_replace_links_and_highlights(document, content_location, link_target):
    content = Content("Lorem", "MD")
    link = Link.prepare(content_location, link_target)
    highlight = Highlight.prepare(content_location)
    document.update_content(content, [link], [highlight])
    assert document.content == content
    assert link in document.links
    assert highlight in document.highlights


def test_can_link_document(document, content_location, link_target):
    link = document.link(content_location, link_target)
    assert link in document.links
    assert document.get_link(link.id) is link


def test_can_delete_document_link(document, content_location, link_target):
    link = document.link(content_location, link_target)
    document.get_link(link.id).delete()
    assert link.deleted
    assert link not in document.links


def test_can_highlight_document(document, content_location):
    highlight = document.highlight(content_location)
    assert highlight in document.highlights


def test_can_delete_document_highlight(document, content_location):
    highlight = document.highlight(content_location)
    document.get_highlight(highlight.id).delete()
    assert highlight.deleted
    assert highlight not in document.highlights


def test_document_link_preview_text_is_title(document):
    assert document.link_preview.text == document.title


def test_document_link_preview_has_no_parent(document):
    assert document.link_preview.parent is None


def test_document_link_preview_text_is_updated_to_changed_title(document):
    document.title = "MyModifiedDocument"
    assert document.link_preview.text == "MyModifiedDocument"


def test_can_delete_document(document):
    document.delete()
    assert document.deleted
