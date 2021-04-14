import typing
import abc
import dataclasses
import lib
import domain


@dataclasses.dataclass(frozen=True)
class LinkPreview:
    title: str
    description: typing.Optional[str]


class LinkReference(abc.ABC):

    @abc.abstractmethod
    @property
    def link_preview(self) -> LinkPreview:
        pass

    @abc.abstractmethod
    def _set_link_preview(self, link_preview: LinkPreview):
        pass

    @abc.abstractmethod
    def _apply_link_preview(self):
        pass

    @link_preview.setter
    def link_preview(self, link_preview: LinkPreview):
        self._set_link_preview(link_preview)
        self._apply_link_preview()


class LinkSource(LinkReference):

    @abc.abstractmethod
    def add_link(self, link: "Link"):
        pass

    @abc.abstractmethod
    def remove_link(self, id_: lib.Id):
        pass

    @abc.abstractmethod
    @property
    def links(self) -> typing.FrozenSet["Link"]:
        pass


class LinkTarget(LinkReference):

    @abc.abstractmethod
    def add_backlink(self, link: "Link"):
        pass

    @abc.abstractmethod
    def remove_backlink(self, id_: lib.Id):
        pass

    @abc.abstractmethod
    @property
    def backlinks(self) -> typing.FrozenSet["Link"]:
        pass


class Link(lib.Entity, domain.document.ContentLocatable):

    def __init__(self,
                 id_: lib.Id,
                 source: domain.document.LinkSource,
                 location: domain.document.ContentLocation,
                 target: domain.document.LinkTarget,
                 ):
        super().__init__(id_)
        self._source = source
        self._location = location
        self._target = target
        self._source_preview = self.source.link_preview
        self._target_preview = self.target.link_preview

    @classmethod
    def create(cls,
               source: domain.document.LinkSource,
               location: domain.document.ContentLocation,
               target: domain.document.LinkTarget,
               ):
        link = cls(lib.Id(), source, location, target)
        source.add_link(link)
        target.add_backlink(link)

    def release(self):
        self.source.remove_link(self.id)
        self.target.remove_backlink(self.id)

    @property
    def source(self):
        return self._source

    @property
    def location(self):
        return self._location

    @property
    def target(self):
        return self._target

    @property
    def source_preview(self):
        return self._source_preview

    def apply_source_preview_update(self):
        self._source_preview = self._source.link_preview

    @property
    def target_preview(self):
        return self._target_preview

    def apply_target_preview_update(self):  # TODO parent needs to be saved
        self._target_preview = self._target.link_preview

    def _info(self):
        return f"id='{self.id}', " \
               f"source='{self.source}', " \
               f"location='{self.location}', " \
               f"target='{self.target}'"
