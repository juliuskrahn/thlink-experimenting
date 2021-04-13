from .content import Content, ContentContainer, ContentLinkParserService
import dataclasses
import typing


class Linkable:

    def __init__(self, backlinks: typing.List[str], **kwargs):
        super().__init__(**kwargs)
        self.backlinks = backlinks


class LinkSource:

    def __init__(self, container: ContentContainer, location: typing.Union[int, str]):
        self._container = container
        self._location = location  # managed by app

    @property
    def container(self):
        return self._container

    @property
    def location(self):
        return self._location


@dataclasses.dataclass(frozen=True)
class Link:
    id_: str
    source: LinkSource
    target: Linkable


class Links(dict):

    def __init__(self, list_: typing.List[Link]):
        super().__init__()
        for link in list_:
            self[link.id_] = link

    @classmethod
    def from_content(cls, content: Content):
        return cls(ContentLinkParserService().parse(content))
