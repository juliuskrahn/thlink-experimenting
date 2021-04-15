import typing
import lib
import domain.document.content
import domain.document.link


class Highlight(lib.Entity,
                domain.document.content.ContentLocatable,
                domain.document.link.Node,
                domain.document.content.ContentContainer,
                ):

    def __init__(self,
                 id_: lib.Id,
                 document: domain.document.Document,
                 location: domain.document.ContentLocation,
                 backlinks: typing.List[domain.document.link.Link],
                 content: domain.document.Content = None,
                 links: typing.List[domain.document.link.Link] = None,
                 ):

        lib.Entity.__init__(self, id_)
        domain.document.content.ContentLocatable.__init__(self, location)

        self._document = document
        self._content = content
        link_preview_description = None
        if self.content:
            link_preview_description = self.content.data
        self._link_preview = domain.document.link.LinkPreview(self.document.title, link_preview_description)

        if links is None:
            links = []
        domain.document.link.Node.__init__(self, links, backlinks)

    @property
    def document(self):
        return self._document

    @property
    def link_preview(self):
        return self._link_preview

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content: typing.Optional[domain.document.Content]):
        self._content = content
        if not CanLinkPolicy.is_satisfied_by(self):
            for link in self.links:
                link.delete()

    @property
    def links(self):
        if CanLinkPolicy.is_satisfied_by(self):
            return super().links
        return None

    def register_link(self, link: domain.document.link.Link):
        assert CanLinkPolicy.is_satisfied_by(self)
        super().register_link(link)

    def _info(self):
        return f"id='{self.id}', " \
               f"document='{self.document}', " \
               f"location='{self.location}'"


class CanLinkPolicy:

    @staticmethod
    def is_satisfied_by(highlight: Highlight):
        return highlight.content is not None
