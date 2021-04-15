import typing
import abc
import dataclasses


@dataclasses.dataclass(frozen=True)
class Content:
    data: typing.Any
    type: str


ContentLocation = typing.NewType("ContentLocation", str)


class ContentContainer(abc.ABC):

    @abc.abstractmethod
    @property
    def content(self):
        pass


class ContentLocatable:

    def __init__(self, location: ContentLocation):
        self._location = location

    @property
    def location(self):
        return self._location
