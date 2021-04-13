from .content import Content
from .link import Linkable, Link
import typing


class Document(Linkable):

    def __init__(self,
                 title: str,
                 tags: typing.List[str],
                 content: Content,
                 backlinks: typing.List[Link],
                 ):
        super().__init__(backlinks)
        self.title = title
        self.tags = tags
        self._content = content
