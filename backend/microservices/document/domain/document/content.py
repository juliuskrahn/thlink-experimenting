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

    @abc.abstractmethod
    @property
    def location(self) -> ContentLocation:
        pass
