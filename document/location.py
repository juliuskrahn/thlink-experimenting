import typing


LocationPositionType = typing.Union[int, str]


class Location:

    def __init__(self, position: LocationPositionType):
        self._position = position

    @property
    def position(self):
        return self._position
