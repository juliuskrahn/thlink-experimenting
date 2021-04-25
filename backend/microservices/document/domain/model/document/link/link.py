from __future__ import annotations
import typing
import abc
import dataclasses
from domain import lib
from ..content import ContentLocatable, ContentLocation
from .policy import TargetIsInSameWorkspaceAsSourcePolicy


class Link(ContentLocatable, lib.ChildEntity):

    def __init__(self,
                 id_: lib.Id,
                 location: ContentLocation,
                 source: typing.Optional[LinkSource],
                 source_link_preview: typing.Optional[LinkPreview],
                 target: typing.Optional[LinkTarget],
                 target_link_preview: typing.Optional[LinkPreview],
                 ):
        lib.ChildEntity.__init__(self, id_)
        ContentLocatable.__init__(self, location)
        self._source = source
        self._target = target
        self._source_preview = source_link_preview
        self._target_preview = target_link_preview
        self._deleted = False

    @classmethod
    def prepare(cls, location: ContentLocation, target: LinkTarget):
        return cls(lib.Id(), location=location, target=target, target_link_preview=target.link_preview,
                   source=None, source_link_preview=None)

    def _complete(self, source: LinkSource):
        assert TargetIsInSameWorkspaceAsSourcePolicy.is_satisfied_by(source, self.target)
        self._source = source
        source._register_link(self)
        self._source_preview = source.link_preview
        self.target._register_backlink(self)

    def delete(self):
        if not self.deleted:
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


@dataclasses.dataclass
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
