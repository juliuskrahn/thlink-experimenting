import typing
from domain import lib
from .content import ContentContainer, Content, ContentLocation
from .link import Node, Link, LinkPreview, LinkTarget
from .highlight import Highlightable, Highlight


class Document(lib.Entity, Node, ContentContainer, Highlightable):

    def __init__(self,
                 id_: lib.Id,
                 title: str,
                 content: Content,
                 links: typing.List[Link],
                 backlinks: typing.List[Link],
                 highlights: typing.List[Highlight],
                 ):

        lib.Entity.__init__(self, id_)
        self._deleted = False

        self._title = title
        self._content = content
        self._link_preview = LinkPreview(self.title, None)

        Node.__init__(self, links, backlinks)

        self._highlights = lib.ChildEntities(highlights)

    @classmethod
    def create(cls,
               title: str,
               content: Content,
               links: typing.List[Link],
               highlights: typing.List[Highlight],
               ):
        return cls(lib.Id(), title, content, links, [], highlights)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title
        self._link_preview.text = title

    @property
    def content(self):
        return self._content

    def update_content(self,
                       content: Content,
                       links: typing.List[Link],
                       highlights: typing.List[Highlight],
                       ):
        self._content = content
        self._links = links
        self._highlights = highlights

    @property
    def link_preview(self):
        return self._link_preview

    def link(self, location: ContentLocation, to: LinkTarget):
        link = Link.create(self, location, to)
        return link

    @property
    def highlights(self) -> typing.ValuesView[Highlight]:
        return self._highlights.view()

    def highlight(self, location: ContentLocation):
        highlight = Highlight.create(self, location)
        return highlight

    def get_highlight(self, id_: lib.Id) -> Highlight:
        return self._highlights.get(id_)

    def delete_highlight(self, id_: lib.Id):
        self.get_highlight(id_).delete()

    def delete(self):
        self._deleted = True
        for highlight in self.highlights:
            highlight.delete()
        for link in self.links:
            link.delete()

    @property
    def deleted(self):
        return self._deleted

    def register_highlight(self, highlight: Highlight):
        self._highlights.register(highlight)

    def unregister_highlight(self, id_: lib.Id):
        self._highlights.unregister(id_)

    def _info(self):
        return f"id='{self._id}', title='{self.title}'"
