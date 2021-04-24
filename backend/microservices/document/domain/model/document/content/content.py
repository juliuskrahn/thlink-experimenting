import typing
import dataclasses


@dataclasses.dataclass
class Content:
    body: typing.Any
    type: str


ContentLocation = typing.NewType("ContentLocation", str)


class ContentLocatable:

    def __init__(self, location: ContentLocation):
        self._location = location

    @property
    def location(self):
        return self._location
