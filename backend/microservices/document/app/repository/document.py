from typing import List
from domain import lib
from domain.model.document import Document, Content, Link, Highlight


class DocumentRepositoryDocument(Document):

    content_id: lib.Id
    version: int

    def _repository_init(self: Document, version: int, content_id: lib.Id):
        self.content_id = content_id
        self.version = version
        self._initial_version = version

    def update_content(self,
                       content: Content,
                       links: List[Link],
                       highlights: List[Highlight],
                       ):
        super().update_content(content, links, highlights)
        if self._initial_version == self.version:
            self.version += 1
