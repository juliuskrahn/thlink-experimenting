from __future__ import annotations
import typing
import abc
import dataclasses
import lib
import domain.document.content


class Link(domain.document.content.ContentLocatable, lib.Entity):

    def __init__(self,
                 id_: lib.Id,
                 source: LinkSource,
                 location: domain.document.content.ContentLocation,
                 target: typing.Optional[LinkTarget],
                 ):
        super().__init__(location)
        super(domain.document.content.ContentLocatable, self).__init__(id_)
        self._source = source
        self._location = location
        self._target = target
        self._source_preview = self.source.link_preview
        self._target_preview = self.target.link_preview if self._target else None
        self._deleted = False

    @classmethod
    def create(cls,
               source: LinkSource,
               location: domain.document.content.ContentLocation,
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

    @abc.abstractmethod
    @property
    def link_preview(self) -> LinkPreview:
        pass

    @abc.abstractmethod
    @property
    def deleted(self) -> bool:
        pass


class LinkSource(LinkReference):

    @abc.abstractmethod
    @property
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

    @abc.abstractmethod
    @property
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
