import typing
import abc
from domain import lib
from .link import Link, LinkPreview, LinkSource, LinkTarget


class Node(LinkSource, LinkTarget):

    def __init__(self, links: typing.List[Link] = None, backlinks: typing.List[Link] = None):
        self._links = lib.ChildEntityManager(links if links else [])
        self._backlinks = lib.ChildEntityManager(backlinks if backlinks else [])

    @property
    def links(self) -> typing.Optional[typing.ValuesView[Link]]:
        return self._links.get_all()

    def get_link(self, id_: lib.Id) -> Link:
        return self._links.get(id_)

    def _register_link(self, link: Link):
        self._links.register(link)

    def _unregister_link(self, id_: lib.Id):
        self._links.unregister(id_)

    def _complete_links(self, links: typing.List[Link]):
        for link in links:
            link._complete(self)

    def _delete_links(self):
        if self.links:
            for link in [*self.links]:
                link.delete()

    @property
    def backlinks(self) -> typing.ValuesView[Link]:
        return self._backlinks.get_all()

    def get_backlink(self, id_: lib.Id) -> Link:
        return self._backlinks.get(id_)

    def _register_backlink(self, link: Link):
        self._backlinks.register(link)

    def _unregister_backlink(self, id_: lib.Id):
        self._backlinks.unregister(id_)

    @property
    @abc.abstractmethod
    def link_preview(self) -> LinkPreview:
        pass
