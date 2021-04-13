from .content import Content, ContentLinkParserService
from .content_container import ContentContainer
from .location import Location
import dataclasses
import typing


class Linkable:

    def __init__(self, backlinks: typing.List[str], **kwargs):
        super().__init__(**kwargs)
        self.backlinks = backlinks


class LinkLocation(Location):

    def __init__(self, container: ContentContainer, position: typing.Union[int, str]):
        super().__init__(position)
        self._container = container

    @property
    def container(self):
        return self._container


@dataclasses.dataclass(frozen=True)
class Link:  # TODO living document link (/ note) -> no id ?
    id_: str
    location: LinkLocation
    to: Linkable


class Links(dict):

    def __init__(self, list_: typing.List[Link]):
        super().__init__()
        for link in list_:
            self[link.id_] = link

    @classmethod
    def from_content(cls, content: Content):
        list_ = [Link() for raw in ContentLinkParserService().parse(content)]
        return cls(list_)
