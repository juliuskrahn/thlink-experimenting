from . import Content
from ..links import Linkable, Links


class ContentContainer(Linkable):

    def __init__(self, content: Content, links: Links, backlinks):
        super().__init__(backlinks)
        self._content = content
        self._links = links

    @property
    def content(self):
        return self._content

    @property
    def links(self):
        return self._links
