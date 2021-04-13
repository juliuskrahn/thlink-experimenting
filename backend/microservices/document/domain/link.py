from .location import Location
import typing


class Linkable:

    def __init__(self, backlinks: typing.List["Link"]):
        self._backlinks = backlinks

    @property
    def backlinks(self):
        return self._backlinks


class Link:

    def __init__(self, location: Location, target: Linkable):
        self._location = location
        self._target = target

    @property
    def location(self):
        return self._location

    @property
    def target(self):
        return self._target
