from domain.model.document import Link


def test_can_set_highlight_note(highlight, content):
    highlight.make_note(content)
    assert highlight.note == content


def test_can_delete_highlight_note(highlight):
    highlight.delete_note()
    assert highlight.note is None


def test_can_set_highlight_note_and_replace_links(highlight, content, content_location, link_target):
    link = Link.prepare(content_location, link_target)
    highlight.make_note(content, [link])
    assert link in highlight.links
    assert highlight.get_link(link.id) is link


def test_highlight_without_note_has_no_links(highlight):
    assert highlight.links is None


def test_highlight_with_note_has_links(highlight_with_note):
    assert len(highlight_with_note.links) >= 0


def test_highlight_link_preview_text_is_none_by_default(highlight):
    assert highlight.link_preview.text is None


def test_highlight_link_preview_text_can_be_set(highlight):
    highlight.link_preview.text = "preview"
    assert highlight.link_preview.text == "preview"


def test_highlight_link_preview_parent_is_parent_document_link_preview(highlight):
    assert highlight.link_preview.parent is highlight.parent.link_preview
