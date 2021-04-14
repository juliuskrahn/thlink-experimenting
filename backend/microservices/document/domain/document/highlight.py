import typing
import lib
import domain


class Highlight(lib.Entity,
                domain.document.ContentLocatable,
                domain.document.LinkTarget,
                domain.document.ContentContainer,
                domain.document.LinkSource,
                ):

    def __init__(self,
                 id_: lib.Id,
                 document: domain.document.Document,
                 location: domain.document.ContentLocation,
                 backlinks: typing.FrozenSet[domain.document.Link],
                 content: domain.document.Content = None,
                 links: typing.FrozenSet[domain.document.Link] = None,
                 ):
        super().__init__(id_)
        self._document = document
        self._location = location
        self._backlinks = backlinks
        self._content = content
        self._links = links
        link_preview_description = None
        if self.content:
            link_preview_description = self.content.data
        self._link_preview = domain.document.LinkPreview(self.document.title, link_preview_description)

        assert HighlightContentPolicy.is_satisfied_by(self)

    @property
    def document(self):
        return self._document

    @property
    def location(self):
        return self._location

    @property
    def link_preview(self):
        return self._link_preview

    def _set_link_preview(self, link_preview: domain.document.LinkPreview):
        self._link_preview = link_preview

    def _apply_link_preview(self):
        for link in self.backlinks:
            link.apply_target_preview_update()

    def add_backlink(self, link: domain.document.Link):
        pass

    def remove_backlink(self, id_: lib.Id):
        pass

    @property
    def backlinks(self):
        return self._backlinks

    def add_link(self, link: domain.document.Link):
        pass

    def remove_link(self, id_: lib.Id):
        pass

    @property
    def links(self):
        return self._links

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content: typing.Optional[domain.document.Content]):
        if content is None:
            self._links = None  # TODO release links
        else:
            if self._links is None:
                self._links = frozenset()
        self._content = content

        assert HighlightContentPolicy.is_satisfied_by(self)

    def _info(self):
        return f"id='{self.id}', " \
               f"document='{self.document}', " \
               f"location='{self.location}'"


class HighlightContentPolicy:

    @staticmethod
    def is_satisfied_by(highlight: Highlight):
        return (highlight.content is None) == (highlight.links is None)
