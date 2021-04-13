import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Location:
    container: typing.Any
    position: typing.Union[int, str]
