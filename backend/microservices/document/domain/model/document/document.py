import typing
from domain import lib
from .content import Content, ContentLocation
from .link import Node, Link, LinkPreview, LinkTarget
from .highlight import Highlightable, Highlight
from . import Workspace


class Document(Node, Highlightable, lib.RootEntity):

    def __init__(self,
                 id_: lib.Id,
                 workspace: Workspace,
                 title: str,
                 tags: typing.List[str],
                 content: Content,
                 links: typing.List[Link],
                 backlinks: typing.List[Link],
                 highlights: typing.List[Highlight],
                 ):
        lib.RootEntity.__init__(self, id_)
        self._workspace = workspace
        self._title = title
        self._tags = tags
        self._content = content
        self._link_preview = LinkPreview(self.title, None)
        Node.__init__(self, links, backlinks)
        self._highlights = lib.ChildEntityManager(highlights)
        self._deleted = False

    @classmethod
    def create(cls,
               workspace: Workspace,
               title: str,
               tags: typing.List[str],
               content: Content,
               links: typing.List[Link],
               highlights: typing.List[Highlight],
               ):
        document = cls(lib.Id(), workspace, title, tags, content, links=[], backlinks=[], highlights=[])
        document._complete_links(links)
        document._complete_highlights(highlights)
        return document

    def delete(self):
        self._deleted = True

    @property
    def deleted(self):
        return self._deleted

    @property
    def workspace(self):
        return self._workspace

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title
        self._link_preview.text = title

    @property
    def tags(self):
        return [*self._tags]

    def tag(self, tag: str):
        self._tags.append(tag)

    def untag(self, tag: str):
        self._tags.remove(tag)

    @property
    def content(self):
        return self._content

    def update_content(self,
                       content: Content,
                       links: typing.List[Link],
                       highlights: typing.List[Highlight],
                       ):
        self._delete_links()
        self._delete_highlights()
        self._content = content
        self._complete_links(links)
        self._complete_highlights(highlights)

    def link(self, location: ContentLocation, to: LinkTarget):
        link = Link.prepare(location, to)
        link._complete(self)
        return link

    def highlight(self, location: ContentLocation):
        highlight = Highlight.prepare(location)
        highlight._complete(self)
        return highlight

    def _complete_highlights(self, highlights: typing.List[Highlight]):
        for highlight in highlights:
            highlight._complete(self)

    def _delete_highlights(self):
        for highlight in [*self.highlights]:
            highlight.delete()

    @property
    def highlights(self) -> typing.ValuesView[Highlight]:
        return self._highlights.get_all()

    def get_highlight(self, id_: lib.Id) -> Highlight:
        return self._highlights.get(id_)

    def _register_highlight(self, highlight: Highlight):
        self._highlights.register(highlight)

    def _unregister_highlight(self, id_: lib.Id):
        self._highlights.unregister(id_)

    @property
    def link_preview(self):
        return self._link_preview

    def _info(self):
        return f"id='{self._id}', title='{self.title}'"
