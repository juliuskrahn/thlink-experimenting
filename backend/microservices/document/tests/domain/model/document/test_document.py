import pytest
from domain.model.document import Document, Content, Highlight, Link, ContentLocation


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


def test_can_create_document_with_links(content, content_location, other_document):
    link = Link.prepare(content_location, other_document)
    document = Document.create("MyDocument", tags=[], content=content,
                               links=[link],
                               highlights=[])
    assert link in document.links
    assert document.get_link(link.id) is link


def test_can_update_document_content_and_replace_links_and_highlights(document, content_location, other_document):
    content = Content("Lorem", "MD")
    link = Link.prepare(content_location, other_document)
    highlight = Highlight.prepare(content_location)
    document.update_content(content, [link], [highlight])
    assert document.content == content
    assert link in document.links
    assert highlight in document.highlights


def test_can_link_document(document, content_location, other_document):
    link = document.link(content_location, other_document)
    assert link in document.links


def test_can_delete_link(document, content_location, other_document):
    link = document.link(content_location, other_document)
    document.get_link(link.id).delete()
    assert link.deleted
    assert link not in document.links


def test_linking_to_another_document_results_in_a_backlink(document, content_location, other_document):
    link = document.link(content_location, other_document)
    assert link in other_document.backlinks


def test_deleting_a_link_removes_the_backlink_from_the_other_document(document, content_location, other_document):
    link = document.link(content_location, other_document)
    document.get_link(link.id).delete()
    assert link not in other_document.backlinks


def test_can_highlight_document(document, content_location):
    highlight = document.highlight(content_location)
    assert highlight in document.highlights


def test_can_delete_highlight(document, content_location):
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


def test_link_source_preview_is_document_link_preview(document, content_location, other_document):
    link = document.link(content_location, other_document)
    assert link.source_preview == document.link_preview


def test_link_target_preview_is_other_document_link_preview(document, content_location, other_document):
    link = document.link(content_location, other_document)
    assert link.target_preview == other_document.link_preview


def test_link_source_preview_is_updated_to_changed_document_link_preview(document, content_location, other_document):
    link = document.link(content_location, other_document)
    document.title = "MyModifiedDocument"
    assert link.source_preview == document.link_preview


def test_link_target_preview_is_updated_to_changed_other_document_link_preview(document, content_location,
                                                                               other_document):
    link = document.link(content_location, other_document)
    other_document.title = "MyOtherModifiedDocument"
    assert link.target_preview == other_document.link_preview


def test_deleting_a_document_that_is_linked_to_from_another_document_makes_this_link_broken(document, content_location,
                                                                                            other_document):
    link = document.link(content_location, other_document)
    other_document.delete()
    assert document.get_link(link.id).broken


def test_deleting_a_document_that_links_to_another_document_removes_these_backlinks(document, content_location,
                                                                                    other_document):
    link = document.link(content_location, other_document)
    document.delete()
    assert link not in other_document.backlinks


def test_can_attach_note_to_highlight(document, content_location, content):
    highlight = document.highlight(content_location)
    highlight.make_note(content)
    assert highlight.note == content


# TODO test highlight...


def test_can_delete_document(document):
    document.delete()
    assert document.deleted
