from typing import List, Callable
from functools import cache
from domain.model.document import Document, Content, Link, Highlight


class DocumentRepositoryDocument(Document):
    version: int
    get_content_body_url: Callable

    def _repository_init(self: Document, version: int, content_body_url_getter: Callable):
        self.version = version
        self._initial_version = version
        self.get_content_body_url = cache(content_body_url_getter)

    def update_content(self,
                       content: Content,
                       links: List[Link],
                       highlights: List[Highlight],
                       ):
        super().update_content(content, links, highlights)
        if self._initial_version == self.version:
            self.version += 1
