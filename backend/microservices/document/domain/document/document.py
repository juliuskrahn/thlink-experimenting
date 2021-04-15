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
                 highlights: typing.List[domain.document.Highlight]
                 ):

        lib.Entity.__init__(self, id_)
        self._deleted = False

        self._title = title
        self._content = content
        self._link_preview = domain.document.link.LinkPreview(self.title, None)

        domain.document.link.Node.__init__(self, links, backlinks)

        self._highlights = {highlight.id: highlight for highlight in highlights}

    def delete(self):
        self._deleted = True
        for highlight in self.highlights:
            highlight.delete()
        for link in self.links:
            link.delete()
        for link in self.backlinks:
            link.delete()  # TODO mark as broken

    @property
    def deleted(self):
        return self._deleted

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title
        self._link_preview.title = title

    @property
    def link_preview(self):
        return self._link_preview

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
    def highlights(self):
        return self._highlights.values()

    def highlight(self, location: domain.document.ContentLocation):
        highlight = domain.document.Highlight.create(self, location)
        return highlight

    def register_highlight(self, highlight: domain.document.Highlight):
        self._highlights[highlight.id] = highlight

    def unregister_highlight(self, highlight: domain.document.Highlight):
        del self._highlights[highlight.id]

    def _info(self):
        return f"id='{self._id}', title='{self.title}'"
