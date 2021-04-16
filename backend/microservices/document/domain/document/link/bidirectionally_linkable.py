import typing
import abc
import lib
from . import LinkSource, LinkTarget, Link, LinkPreview


class BiDirectionallyLinkable(LinkSource, LinkTarget):

    def __init__(self, links: typing.List[Link], backlinks: typing.List[Link]):
        self._links = lib.ChildEntities(links)
        self._backlinks = lib.ChildEntities(backlinks)

    @property
    @abc.abstractmethod
    def link_preview(self) -> LinkPreview:
        pass

    @property
    def links(self) -> typing.ValuesView[Link]:
        return self._links.view()

    def get_link(self, id_: lib.Id) -> Link:
        return self._links.get(id_)

    def delete_link(self, id_: lib.Id):
        self.get_link(id_).delete()

    def register_link(self, link: Link):
        self._links.register(link)

    def unregister_link(self, id_: lib.Id):
        self._links.unregister(id_)

    @property
    def backlinks(self) -> typing.ValuesView[Link]:
        return self._backlinks.view()

    def get_backlink(self, id_: lib.Id) -> Link:
        return self._backlinks.get(id_)

    def register_backlink(self, link: Link):
        self._backlinks.register(link)

    def unregister_backlink(self, id_: lib.Id):
        self._backlinks.unregister(id_)
