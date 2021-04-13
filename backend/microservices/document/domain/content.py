from .link import Link
from .highlight import Highlight
import typing


class Content:

    def __init__(self,
                 value,
                 content_type: str,
                 living: bool,
                 links: typing.List[Link] = None,
                 highlights: typing.List[Highlight] = None,
                 ):
        self._value = value  # (actual content) managed by app
        self._type = content_type  # managed by app
        self._living = living  # dynamic/ editable
        if self.living:
            self._links = Store(self._parse_links())  # links generated from content (value) (parsed as text)
            self._highlights = Store()  # no highlights
        else:
            assert links is not None
            self._links = Store(links, lambda link: link.id)  # links managed by app
            assert highlights is not None
            self._highlights = Store(links, lambda highlight: highlight.id)  # highlights managed by app

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        assert self.living
        self._value = value
        self._links = Store(self._parse_links())

    def _parse_links(self):
        return []

    @property
    def type(self):
        return self._type

    @property
    def living(self):
        return self._living

    @property
    def links(self):
        return self._links.view()

    @property
    def highlights(self):
        return self._highlights.view()


class Store:

    def __init__(self,
                 items: typing.Optional[typing.List] = None,
                 living_key: typing.Optional[typing.Callable] = None,
                 ):
        self._living_key = living_key
        if items is None:
            self._solution = None
        elif self.living:
            self._solution = {living_key(item): item for item in items}
        else:
            self._solution = [*items]

    def view(self):
        if type(self._solution) is dict:
            return [*self._solution.values()]
        if type(self._solution) is list:
            return [*self._solution]
        return None

    @property
    def living(self):
        return callable(self._living_key) and self._solution is not None

    def add(self, item):
        assert self.living
        self._solution[self._living_key(item)] = item

    def remove(self, key):
        assert self.living
        del self._solution[key]
