import typing
import abc
from . import LinkSource, LinkTarget, Link, LinkPreview


class Node(LinkSource, LinkTarget):

    def __init__(self, links: typing.List[Link], backlinks: typing.List[Link]):
        self._links = {link.id: link for link in links}
        self._backlinks = {link.id: link for link in backlinks}

    @abc.abstractmethod
    @property
    def link_preview(self) -> LinkPreview:
        pass

    @property
    def backlinks(self):
        return self._backlinks.values()

    def register_backlink(self, link: Link):
        self._backlinks[link.id] = link

    def unregister_backlink(self, link: Link):
        del self._backlinks[link.id]

    @property
    def links(self):
        return self._links.values()

    def register_link(self, link: Link):
        self._links[link.id] = link

    def unregister_link(self, link: Link):
        del self._links[link.id]
