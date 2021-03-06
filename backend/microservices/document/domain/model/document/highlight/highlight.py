from __future__ import annotations
import typing
import abc
from domain import lib
from ..content import ContentLocatable, ContentLocation, Content
from ..link import Node, Link, LinkPreview, LinkReference


class Highlight(Node, ContentLocatable, lib.ChildEntity):

    def __init__(self,
                 id_: lib.Id,
                 location: ContentLocation,
                 parent: typing.Optional[Highlightable],
                 link_preview: LinkPreview,
                 links: typing.Optional[typing.List[Link]],
                 backlinks: typing.List[Link],
                 note: typing.Optional[Content],
                 ):
        lib.ChildEntity.__init__(self, id_)
        ContentLocatable.__init__(self, location)
        self._parent = parent
        Node.__init__(self, links if links else [], backlinks)
        self._note = note
        self._link_preview = link_preview
        self._deleted = False

    @classmethod
    def prepare(cls, location: ContentLocation, link_preview_text: str = None):
        return cls(
            lib.Id(),
            location=location,
            links=None,
            backlinks=[],
            note=None,
            parent=None,
            link_preview=LinkPreview(text=link_preview_text, parent=None),
        )

    def _complete(self, parent: Highlightable):
        self._parent = parent
        parent._register_highlight(self)
        self._link_preview.parent = parent.link_preview

    def delete(self):
        if not self.deleted:
            self._deleted = True
            self.parent._unregister_highlight(self.id)

    @property
    def completed(self):
        return bool(self.parent)

    @property
    def deleted(self):
        return self._deleted or self.parent.deleted

    def make_note(self, note: Content, links: typing.List[Link] = None):
        self._delete_links()
        self._note = note
        if links:
            self._complete_links(links)

    def delete_note(self):
        self._delete_links()
        self._note = None

    @property
    def note(self):
        return self._note

    @property
    def parent(self):
        return self._parent

    @property
    def links(self) -> typing.Optional[typing.ValuesView[Link]]:
        if HighlightIsLinkSourcePolicy.is_satisfied_by(self):
            return super().links
        return None

    def _register_link(self, link: Link):
        if not HighlightIsLinkSourcePolicy.is_satisfied_by(self):
            raise lib.DomainError(f"{self} can't be a link source.")
        super()._register_link(link)

    @property
    def link_preview(self):
        return self._link_preview

    def _info(self):
        return f"id='{self.id}', " \
               f"parent='{self.parent}', " \
               f"location='{self.location}'"


class HighlightIsLinkSourcePolicy:

    @staticmethod
    def is_satisfied_by(highlight: Highlight):
        return highlight.note is not None


class Highlightable(LinkReference):

    @abc.abstractmethod
    def _register_highlight(self, highlight: Highlight):
        pass

    @abc.abstractmethod
    def _unregister_highlight(self, id_: lib.Id):
        pass
