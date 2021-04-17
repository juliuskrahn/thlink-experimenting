import typing
from domain import lib
from domain.model.document.link import LinkSource, LinkTarget, LinkPreview, Link, Node
from domain.model.document.highlight import Highlightable, Highlight


class LinkReferenceImplementation:

    def __init__(self, link_preview: LinkPreview, deleted: bool):
        self._link_preview = link_preview
        self._deleted = deleted

    @property
    def link_preview(self):
        return self._link_preview

    def delete(self):
        self._deleted = True

    @property
    def deleted(self):
        return self._deleted


class LinkSourceImplementation(LinkReferenceImplementation, LinkSource):

    def __init__(self,
                 links: typing.List[Link],
                 backlinks: typing.List[Link],  # ignored
                 link_preview: LinkPreview,
                 deleted=False,
                 ):
        LinkReferenceImplementation.__init__(self, link_preview, deleted)
        self._links = {backlink.id: backlink for backlink in links}

    @property
    def links(self):
        return self._links.values()

    def register_link(self, link: Link):
        self._links[link.id] = link

    def unregister_link(self, id_: lib.Id):
        del self._links[id_]


class LinkTargetImplementation(LinkReferenceImplementation, LinkTarget):

    def __init__(self,
                 links: typing.List[Link],  # ignored
                 backlinks: typing.List[Link],
                 link_preview: LinkPreview,
                 deleted=False,
                 ):
        LinkReferenceImplementation.__init__(self, link_preview, deleted)
        self._backlinks = {backlink.id: backlink for backlink in backlinks}

    @property
    def backlinks(self):
        return self._backlinks.values()

    def register_backlink(self, link: Link):
        self._backlinks[link.id] = link

    def unregister_backlink(self, id_: lib.Id):
        del self._backlinks[id_]


class LinkNodeImplementation(LinkReferenceImplementation, Node):

    def __init__(self,
                 links: typing.List[Link],
                 backlinks: typing.List[Link],
                 link_preview: LinkPreview,
                 deleted=False,
                 ):
        LinkReferenceImplementation.__init__(self, link_preview, deleted)
        Node.__init__(self, links, backlinks)


class HighlightableImplementation(Highlightable):

    def __init__(self, highlights: typing.List[Highlight], link_preview: LinkPreview, deleted=False):
        self._highlights = {highlight.id: highlight for highlight in highlights}
        self._link_preview = link_preview
        self._deleted = deleted

    @property
    def link_preview(self):
        return self._link_preview

    def delete(self):
        self._deleted = True

    @property
    def deleted(self):
        return self._deleted

    def register_highlight(self, highlight: Highlight):
        self._highlights[highlight.id] = highlight

    def unregister_highlight(self, id_: lib.Id):
        del self._highlights[id_]
