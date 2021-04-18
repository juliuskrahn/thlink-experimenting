from __future__ import annotations
import typing
import abc
import dataclasses
from domain import lib
from ..content import ContentLocatable, ContentLocation


class Link(ContentLocatable, lib.ChildEntity):

    def __init__(self,
                 id_: lib.Id,
                 location: ContentLocation,
                 source: typing.Optional[LinkSource],
                 target: typing.Optional[LinkTarget]
                 ):
        lib.ChildEntity.__init__(self, id_)
        ContentLocatable.__init__(self, location)
        self._source = source
        self._target = target
        self._source_preview = source.link_preview if source else None
        self._target_preview = target.link_preview if target else None
        self._deleted = False

    @classmethod
    def prepare(cls, location: ContentLocation, target: LinkTarget):
        return cls(lib.Id(), location=location, source=None, target=target)

    def _complete(self, source: LinkSource):
        self._source = source
        source._register_link(self)
        self._source_preview = source.link_preview
        self.target._register_backlink(self)

    def delete(self):
        self._deleted = True
        self.source._unregister_link(self.id)
        self.target._unregister_backlink(self.id)

    @property
    def completed(self):
        return bool(self.source)

    @property
    def deleted(self):
        return self._deleted or self.source.deleted

    @property
    def broken(self):
        return self.target is None or self.target.deleted

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

    def _info(self):
        return f"id='{self.id}', " \
               f"source='{self.source}', " \
               f"location='{self.location}', " \
               f"target='{self.target}'"


@dataclasses.dataclass()
class LinkPreview:
    text: typing.Optional[str]
    parent: typing.Optional[LinkPreview]


class LinkReference:

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
    def _register_link(self, link: Link):
        # called by link._complete
        pass

    @abc.abstractmethod
    def _unregister_link(self, id_: lib.Id):
        # called by link.delete
        pass


class LinkTarget(LinkReference):

    @property
    @abc.abstractmethod
    def backlinks(self) -> typing.ValuesView[Link]:
        pass

    @abc.abstractmethod
    def _register_backlink(self, link: Link):
        # called by link._complete
        pass

    @abc.abstractmethod
    def _unregister_backlink(self, id_: lib.Id):
        # called by link.delete
        pass


class Node(LinkSource, LinkTarget):

    def __init__(self, links: typing.List[Link] = None, backlinks: typing.List[Link] = None):
        self._links = lib.ChildEntityManager(links if links else [])
        self._backlinks = lib.ChildEntityManager(backlinks if backlinks else [])

    def link(self, location: ContentLocation, to: LinkTarget):
        link = Link.prepare(location, to)
        link._complete(self)
        return link

    @property
    def links(self) -> typing.ValuesView[Link]:
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
