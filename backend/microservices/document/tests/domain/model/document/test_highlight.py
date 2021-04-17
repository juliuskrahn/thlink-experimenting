from domain import lib
from domain.model.document.content import Content
from tests.domain.model.document.implementations import LinkTargetImplementation


class TestHighlightCreation:

    @staticmethod
    def subtest_independent_from_content(highlight_child, highlight_parent, content_location):
        assert isinstance(highlight_child.id, lib.Id)
        assert highlight_child.parent == highlight_parent
        assert highlight_child.link_preview.parent == highlight_parent.link_preview
        assert highlight_child.location == content_location
        assert not highlight_child.deleted
        assert highlight_child in highlight_parent.highlights
        assert not len(highlight_child.backlinks)

    def test_without_content(self, highlight_child, highlight_parent, content_location):
        self.subtest_independent_from_content(highlight_child, highlight_parent, content_location)
        assert highlight_child.content is None
        assert highlight_child.links is None

    def test_with_content(self,
                          highlight_child_with_content,
                          highlight_parent,
                          content_location,
                          content
                          ):
        self.subtest_independent_from_content(highlight_child_with_content, highlight_parent, content_location)
        assert highlight_child_with_content.content == content
        assert not len(highlight_child_with_content.links)


class TestHighlightContentUpdateBehaviour:

    def test_content_gets_updated(self, highlight_child_with_content):
        new_content = Content("new content", "md")
        highlight_child_with_content.content = new_content
        assert highlight_child_with_content.content == new_content

    def test_from_no_content_to_content(self, highlight_child, content):
        highlight_child.content = content
        assert highlight_child.content == content
        assert not len(highlight_child.links)

    def test_from_content_to_no_content(self, highlight_child_with_content):
        highlight_child_with_content.delete_content_and_links()
        assert highlight_child_with_content.content is None
        assert highlight_child_with_content.links is None

    def test_delete_links(self, highlight_child_with_content, content_location, link_preview):
        link_target = LinkTargetImplementation([], [], link_preview)
        link = highlight_child_with_content.link(content_location, link_target)
        highlight_child_with_content.delete_links()
        assert link.deleted
        assert link not in highlight_child_with_content.links


class TestHighlightDeletion:

    def test_deletion(self, highlight_child):
        highlight_child.delete()
        assert highlight_child.deleted

    def test_deleted_when_parent_deleted(self, highlight_parent, highlight_child):
        highlight_parent.delete()
        assert highlight_child.deleted
