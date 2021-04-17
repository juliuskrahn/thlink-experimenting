from __future__ import annotations
import typing
import abc
from domain import lib
from ..content import ContentLocatable, ContentLocation, Content
from ..link import Node, Link, LinkPreview, LinkTarget


class Highlightable:

    @property
    @abc.abstractmethod
    def link_preview(self):
        pass

    @property
    @abc.abstractmethod
    def deleted(self):
        pass

    @abc.abstractmethod
    def register_highlight(self, highlight: Highlight):
        pass

    @abc.abstractmethod
    def unregister_highlight(self, id_: lib.Id):
        pass


class Highlight(lib.Entity, ContentLocatable, Node):

    def __init__(self,
                 id_: lib.Id,
                 parent: Highlightable,
                 location: ContentLocation,
                 backlinks: typing.List[Link],
                 content: Content = None,
                 links: typing.List[Link] = None,
                 ):

        lib.Entity.__init__(self, id_)
        self._deleted = False

        ContentLocatable.__init__(self, location)

        self._parent = parent
        self._content = content
        link_preview_text = None
        if self.content:
            link_preview_text = self.content.body
        self._link_preview = LinkPreview(link_preview_text, self.parent.link_preview)

        if links is None:
            links = []
        Node.__init__(self, links, backlinks)

    @classmethod
    def create(cls, parent: Highlightable, location: ContentLocation):
        highlight = cls(lib.Id(), parent, location, [])
        parent.register_highlight(highlight)
        return highlight

    @property
    def parent(self):
        return self._parent

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content: Content):
        assert content, "To delete the content (set content to None) call delete_content_and_links"
        self._content = content
        self._link_preview.text = content.body

    def delete_content_and_links(self):
        self.delete_links()
        self._content = None
        self._link_preview.text = None

    def delete_links(self):
        for link in [*self.links]:
            link.delete()

    @property
    def link_preview(self):
        return self._link_preview

    def link(self, location: ContentLocation, to: LinkTarget):
        assert HighlightLinkSourcePolicy.is_satisfied_by(self)
        link = Link.create(self, location, to)
        return link

    @property
    def links(self) -> typing.Optional[typing.ValuesView[Link]]:
        if HighlightLinkSourcePolicy.is_satisfied_by(self):
            return super().links
        return None

    def register_link(self, link: Link):
        assert HighlightLinkSourcePolicy.is_satisfied_by(self)
        super().register_link(link)

    def delete(self):
        self._deleted = True
        self.parent.unregister_highlight(self.id)

    @property
    def deleted(self):
        return self._deleted or self.parent.deleted

    def _info(self):
        return f"id='{self.id}', " \
               f"parent='{self.parent}', " \
               f"location='{self.location}'"


class HighlightLinkSourcePolicy:

    @staticmethod
    def is_satisfied_by(highlight: Highlight):
        return highlight.content is not None
