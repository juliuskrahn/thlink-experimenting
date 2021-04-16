import typing
import lib
import domain.document.content
import domain.document.link


class Document(lib.Entity,
               domain.document.link.Node,
               domain.document.content.ContentContainer,
               ):

    def __init__(self,
                 id_: lib.Id,
                 title: str,
                 content: domain.document.Content,
                 links: typing.List[domain.document.link.Link],
                 backlinks: typing.List[domain.document.link.Link],
                 highlights: typing.List[domain.document.Highlight],
                 ):

        lib.Entity.__init__(self, id_)
        self._deleted = False

        self._title = title
        self._content = content
        self._link_preview = domain.document.link.LinkPreview(self.title, None)

        domain.document.link.Node.__init__(self, links, backlinks)

        self._highlights = lib.ChildEntities(highlights)

    @classmethod
    def create(cls,
               title: str,
               content: domain.document.Content,
               links: typing.List[domain.document.link.Link],
               highlights: typing.List[domain.document.Highlight],
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
                       content: domain.document.Content,
                       links: typing.List[domain.document.Link],
                       highlights: typing.List[domain.document.Highlight],
                       ):
        self._content = content
        self._links = links
        self._highlights = highlights

    @property
    def link_preview(self):
        return self._link_preview

    def link(self, location: domain.document.content.ContentLocation, to: domain.document.link.LinkTarget):
        link = domain.document.link.Link.create(self, location, to)
        return link

    @property
    def highlights(self) -> typing.ValuesView[domain.document.Highlight]:
        return self._highlights.view()

    def highlight(self, location: domain.document.ContentLocation):
        highlight = domain.document.Highlight.create(self, location)
        return highlight

    def get_highlight(self, id_: lib.Id) -> domain.document.Highlight:
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

    def register_highlight(self, highlight: domain.document.Highlight):
        self._highlights.register(highlight)

    def unregister_highlight(self, id_: lib.Id):
        self._highlights.unregister(id_)

    def _info(self):
        return f"id='{self._id}', title='{self.title}'"
