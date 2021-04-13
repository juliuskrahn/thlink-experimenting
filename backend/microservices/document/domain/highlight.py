from .content import Content
from .link import Linkable, Link
from .location import Location
import typing


class Highlight(Linkable):

    def __init__(self, location: Location, backlinks: typing.List[Link], content: typing.Optional[Content] = None):
        super().__init__(backlinks)
        self._location = location
        self.content = content

    @property
    def location(self):
        return self._location
