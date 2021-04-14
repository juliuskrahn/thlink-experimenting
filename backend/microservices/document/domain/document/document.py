import typing
import lib
import domain.document


class Document(lib.Entity, domain.document.ContentContainer, domain.document.LinkTarget):  # TODO

    def __init__(self,
                 id_: lib.Id,
                 title: str,
                 tags: typing.List[str],
                 content: domain.document.Content,
                 links: typing.List[domain.document.Link],
                 backlinks: typing.FrozenSet[domain.document.Link],
                 highlights: typing.List[domain.document.Highlight],
                 ):
        super().__init__(id_)
        self.title = title
        self.tags = tags
        self._content = content
        self.links = links
        self._backlinks = backlinks
        self.highlights = highlights

    @property
    def content(self):
        return self._content

    def update_content(self,
                       content: domain.document.Content,
                       links: typing.List[domain.document.Link],
                       highlights: typing.List[domain.document.Highlight],
                       ):
        self._content = content
        self.links = links
        self.highlights = highlights

    @property
    def backlinks(self):
        return self._backlinks

    def _info(self):
        return f"id='{self._id}', title='{self.title}'"
