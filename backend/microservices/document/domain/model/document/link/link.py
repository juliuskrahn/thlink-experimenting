from __future__ import annotations
import typing
import abc
import dataclasses
from domain import lib
from ..content import ContentLocatable, ContentLocation


class Link(ContentLocatable, lib.Entity):

    def __init__(self,
                 id_: lib.Id,
                 source: LinkSource,
                 location: ContentLocation,
                 target: typing.Optional[LinkTarget],
                 ):
        super().__init__(location)
        super(ContentLocatable, self).__init__(id_)
        self._source = source
        self._location = location
        self._target = target
        self._source_preview = self.source.link_preview
        self._target_preview = self.target.link_preview if self._target else None
        self._deleted = False

    @classmethod
    def create(cls,
               source: LinkSource,
               location: ContentLocation,
               target: LinkTarget,
               ):
        link = cls(lib.Id(), source, location, target)
        source.register_link(link)
        target.register_backlink(link)
        return link

    def delete(self):
        self._deleted = True
        self.source.unregister_link(self.id)
        self.target.unregister_backlink(self.id)

    @property
    def deleted(self):
        return self._deleted

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def source_preview(self):
        return self._source_preview

    @property
    def target_preview(self):
        return self._target_preview

    @property
    def broken(self):
        return self.target is None or self.target.deleted

    def _info(self):
        return f"id='{self.id}', " \
               f"source='{self.source}', " \
               f"location='{self.location}', " \
               f"target='{self.target}'"


@dataclasses.dataclass()
class LinkPreview:
    text: typing.Optional[str]
    parent: typing.Optional[LinkPreview]


class LinkReference(abc.ABC):

    @property
    @abc.abstractmethod
    def link_preview(self) -> LinkPreview:
        pass

    @property
    @abc.abstractmethod
    def deleted(self) -> bool:
        pass


class LinkSource(LinkReference):

    @property
    @abc.abstractmethod
    def links(self) -> typing.ValuesView[Link]:
        pass

    @abc.abstractmethod
    def register_link(self, link: Link):
        # should be called by link
        pass

    @abc.abstractmethod
    def unregister_link(self, id_: lib.Id):
        # should be called by link
        pass


class LinkTarget(LinkReference):

    @property
    @abc.abstractmethod
    def backlinks(self) -> typing.ValuesView[Link]:
        pass

    @abc.abstractmethod
    def register_backlink(self, link: Link):
        # should be called by link
        pass

    @abc.abstractmethod
    def unregister_backlink(self, id_: lib.Id):
        # should be called by link
        pass


class Node(LinkSource, LinkTarget):

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
