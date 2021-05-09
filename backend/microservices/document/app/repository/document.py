from typing import List, Callable
from functools import cache
from domain.model.document import Document, Content, Link, Highlight


class DocumentRepositoryDocument(Document):

    def _repository_init(self: Document, version: int, content_body_url_getter: Callable):
        self._version = version
        self._initial_version = version
        self._content_body_url_getter = content_body_url_getter

    @property
    def version(self):
        return self._version

    @property
    @cache
    def content_body_url(self):
        return self._content_body_url_getter()

    def update_content(self,
                       content: Content,
                       links: List[Link],
                       highlights: List[Highlight],
                       ):
        super().update_content(content, links, highlights)
        if self._initial_version == self._version:
            self._version += 1
