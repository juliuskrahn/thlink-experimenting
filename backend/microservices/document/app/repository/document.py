from __future__ import annotations
import typing
from copy import deepcopy
import functools
from domain import lib
from domain.model.document.link import LinkPreview
from domain.model.document import Document, Workspace, Link, Highlight, Content, ContentLocation
from domain.model.document import DocumentRepository as AbstractDocumentRepository
from .db import DB, ItemKey, ExpectationNotMet
from .object_storage import ObjectStorage


class DocumentRepository(AbstractDocumentRepository):

    def __init__(self):
        documents_type = typing.Dict[[lib.Id, Workspace]: Document]
        self._documents: documents_type = {}
        self._documents_loaded: documents_type = {}
        self._db = DB()
        self._object_storage = ObjectStorage()
        self._document_factory = DocumentFactory(self)
        self._document_serializer = DocumentSerializer()

    def get(self, id_: lib.Id, workspace: Workspace) -> Document:
        document = self._documents.get((id_, workspace))
        if document:
            return document
        raw_document = self._db.get_item(ItemKey("workspace", workspace, secondary=ItemKey("id", id_)))
        document = self._document_factory.build_document(
            raw_document,
            content_body_getter_factory=lambda content_id: self._object_storage.get(content_id),
        )
        self._documents[(document.id, document.workspace)] = document
        self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return document

    def add(self, document: Document):
        self._documents[(document.id, document.workspace)] = document
        DocumentRepositoryDocument._repository_init(document, version=-1, content_id=lib.Id())

    def get_all_in_workspace(self, workspace: Workspace) -> typing.List[Document]:
        for document in self._documents_loaded:
            if document.workspace == workspace:
                assert ValueError("Workspace is already partially loaded")
        raw_documents = self._db.query_items(ItemKey("workspace", workspace))
        documents = []
        for raw_document in raw_documents:
            document = self._document_factory.build_document(
                raw_document,
                content_body_getter_factory=lambda content_id: self._object_storage.get(content_id),
            )
            documents.append(document)
            self._documents[(document.id, document.workspace)] = document
            self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return documents

    def _save(self):
        for document in set(self._collect_dirty_documents()):
            self._save_document(document)

    def _save_document(self, document: typing.Union[Document, DocumentRepositoryDocument]):
        document_loaded = self._documents_loaded.get((document.id, document.workspace))
        if document.deleted:
            if document_loaded:
                self._db.delete(ItemKey("workspace", document.workspace, secondary=ItemKey("id", document.id)))
                self._object_storage.delete(document.content_id)
        elif document_loaded and document_loaded.content == document.content:
            self._db.update(
                key=ItemKey("workspace", document.workspace, secondary=ItemKey("id", document.id)),
                item=self._document_serializer.serialize_document(document),
                old_item=self._document_serializer.serialize_document(document_loaded),
            )
        else:
            document.version += 1
            try:
                self._db.put(self._document_serializer.serialize_document(document),
                             expected={"version": document.version})
            except ExpectationNotMet:
                raise DocumentModifiedByOtherUser
            self._object_storage.put(document.content_id, document.content.body)

    def _document_is_dirty(self, document: Document):
        return self._document_serializer.serialize_document(
                    self._documents_loaded.get((document.id, document.workspace))
                ) \
               != self._document_serializer.serialize_document(document)

    def _collect_dirty_documents(self) -> typing.Iterable[Document]:
        for document in self._documents.values():
            if self._document_is_dirty(document):
                for indirect in self._collect_indirect_dirty_documents(document):
                    yield indirect
                yield document

    def _collect_indirect_dirty_documents(self, document: Document) -> typing.Iterable[Document]:
        document_loaded = self._documents_loaded.get((document.id, document.workspace))
        if not document_loaded:
            raise StopIteration

        document_link_targets_are_dirty = document_loaded.link_preview != document.link_preview

        def highlight_link_targets_are_dirty(highlight):
            loaded_highlight = document_loaded.get_highlight(highlight.id)
            return loaded_highlight and loaded_highlight.links \
                and loaded_highlight.link_preview != highlight.link_preview

        if document_link_targets_are_dirty:
            for link in document.links:
                yield link.target

        for document_highlight in document.highlights:
            if highlight_link_targets_are_dirty(document_highlight):
                for link in document_highlight.links:
                    yield link.target


class DocumentFactory:

    def __init__(self, document_repository: DocumentRepository):
        self._document_repository = document_repository
        fragments_type = typing.Dict[[lib.Id, Workspace, lib.Id]: Document]
        self._fragment_links: fragments_type = {}
        self._fragment_link_previews: fragments_type = {}

    def build_document(self, data: typing.Dict, content_body_getter_factory: typing.Callable)\
            -> DocumentRepositoryDocument:
        document_id = lib.Id(data["id"])
        workspace = Workspace(data["workspace"])
        content_id = lib.Id(data["content"]["id"])
        document_link_preview = self._get_link_preview(document_id, workspace, highlight_id=None,
                                                       factory_fn=lambda: LinkPreview(data["title"], None))
        content = Content(
            body=self._cached_property(content_body_getter_factory(content_id)),
            type=data["content"]["type"],
        )
        links = [self._get_link(lib.Id(link_id), link_data, document_id, workspace, document_link_preview)
                 for link_id, link_data in data["links"].items()]
        backlinks = [self._get_link(lib.Id(link_id), link_data, document_id, workspace, document_link_preview)
                     for link_id, link_data in data["backlinks"].items()]
        highlights = [self._get_highlight(document_id, workspace, document_link_preview,
                                          lib.Id(highlight_id), highlight_data)
                      for highlight_id, highlight_data in data["highlights"].items()]
        document = DocumentRepositoryDocument(
            id_=document_id,
            workspace=workspace,
            title=data["title"],
            link_preview=document_link_preview,
            tags=data["tags"],
            content=content,
            links=links,
            backlinks=backlinks,
            highlights=highlights,
        )
        document._repository_init(data["version"], content_id)
        return document

    def _get_link(self,
                  link_id: lib.Id,
                  link_data,
                  known_document_id,
                  known_workspace,
                  known_link_preview,
                  known_highlight_id=None,
                  ):
        unknown = "target" if "target" in link_data else "source"
        link = self._fragment_links.get(link_id)
        if link:
            return link
        unknown_document_id = lib.Id(link_data[unknown]["document_id"])
        unknown_workspace = Workspace(link_data[unknown]["workspace"])
        unknown_highlight_id = link_data[unknown].get("highlight_id")
        if unknown_highlight_id:
            unknown_highlight_id = lib.Id(unknown_highlight_id)
            unknown_link_preview = self._get_link_preview(
                unknown_document_id,
                unknown_workspace,
                unknown_highlight_id,
                lambda:
                LinkPreview(link_data[unknown]["link_preview"]["highlight"],
                            self._get_link_preview(
                                unknown_document_id,
                                unknown_workspace,
                                None,
                                lambda: LinkPreview(link_data[unknown]["link_preview"]["document"], None)),
                            ),
            )
        else:
            unknown_link_preview = self._get_link_preview(
                unknown_document_id,
                unknown_workspace,
                None,
                lambda: LinkPreview(link_data[unknown]["link_preview"]["document"], None),
            )
        known_ref_property = self._ref_property(known_document_id, known_workspace, known_highlight_id)
        unknown_ref_property = self._ref_property(unknown_document_id, unknown_workspace, unknown_highlight_id)
        link = DocumentRepositoryLink(
            id_=link_id,
            location=ContentLocation(link_data["location"]),
            source=known_ref_property if unknown == "target" else unknown_ref_property,
            source_link_preview=known_link_preview if unknown == "target" else unknown_link_preview,
            target=unknown_ref_property if unknown == "target" else known_ref_property,
            target_link_preview=unknown_link_preview if unknown == "target" else known_link_preview,
        )
        link._repository_init(
            source_document_id=known_document_id if unknown == "target" else unknown_document_id,
            source_workspace=known_workspace if unknown == "target" else unknown_workspace,
            target_document_id=unknown_document_id if unknown == "target" else known_document_id,
            target_workspace=unknown_workspace if unknown == "target" else known_workspace,
            source_highlight_id=known_highlight_id if unknown == "target" else unknown_highlight_id,
            target_highlight_id=unknown_highlight_id if unknown == "target" else known_highlight_id,
        )
        self._fragment_links[link_id] = link
        return link

    def _get_highlight(self, document_id, workspace, document_link_preview,
                       highlight_id: lib.Id, highlight_data) -> Highlight:
        link_preview = self._get_link_preview(document_id, workspace, highlight_id,
                                              factory_fn=lambda: LinkPreview(highlight_data["link_preview"],
                                                                             document_link_preview))
        links = [self._get_link(lib.Id(link_id), link_data, document_id, workspace, link_preview, highlight_id)
                 for link_id, link_data in highlight_data["links"].items()]
        backlinks = [self._get_link(lib.Id(link_id), link_data, document_id, workspace, link_preview, highlight_id)
                     for link_id, link_data in highlight_data["backlinks"].items()]
        return Highlight(
            id_=highlight_id,
            location=ContentLocation(highlight_data["location"]),
            parent=self._ref_property(document_id, workspace),
            link_preview=link_preview,
            links=links,
            backlinks=backlinks,
            note=highlight_data["note"],
        )

    def _get_link_preview(self, document_id: lib.Id, workspace: Workspace, highlight_id: typing.Optional[lib.Id],
                          factory_fn: typing.Callable):
        link_preview = self._fragment_link_previews.get((document_id, workspace, highlight_id))
        if not link_preview:
            link_preview = factory_fn()
            self._fragment_link_previews[(document_id, workspace, highlight_id)] = link_preview
        return link_preview

    @staticmethod
    def _cached_property(getter: typing.Callable):
        return property(functools.cache(lambda _: getter()))

    def _ref_property(self, document_id: lib.Id, workspace: Workspace, highlight_id: lib.Id = None):
        @property
        def ref_property(_):
            document = self._document_repository.get(document_id, workspace)
            if highlight_id:
                return document.get_highlight(highlight_id)
            return document
        return ref_property


class DocumentSerializer:

    def serialize_document(self, document: DocumentRepositoryDocument) -> typing.Dict:
        links = self._serialize_entities(document.links, self._serialize_link)
        backlinks = self._serialize_entities(document.backlinks, self._serialize_backlink)
        highlights = self._serialize_entities(document.highlights, self._serialize_highlight)
        return {
            "id": document.id,
            "workspace": document.workspace,
            "title": document.title,
            "tags": document.tags,
            "links": links,
            "backlinks": backlinks,
            "highlights": highlights,
            "content_id": document.content_id,
            "version": document.version,
        }

    @staticmethod
    def _serialize_entities(collection: typing.Iterable, serialize_fn: typing.Callable):
        serialized_collection = {}
        for entity in collection:
            id_, data = serialize_fn(entity)
            serialized_collection[id_] = data
        return serialized_collection

    @staticmethod
    def _serialize_link(link: DocumentRepositoryLink) -> typing.Tuple[str, typing.Dict]:
        data = {
            "location": link.location,
            "target": {
                "document_id": link.target_document_id,
                "workspace": link.target_workspace,
                "link_preview": link.target_preview,
            },
        }
        if link.target_highlight_id:
            data["target"]["highlight_id"] = link.target_highlight_id
        return link.id, data

    @staticmethod
    def _serialize_backlink(link: DocumentRepositoryLink) -> typing.Tuple[str, typing.Dict]:
        data = {
            "location": link.location,
            "source": {
                "document_id": link.source_document_id,
                "workspace": link.source_workspace,
                "link_preview": link.source_preview,
            },
        }
        if link.source_highlight_id:
            data["source"]["highlight_id"] = link.source_highlight_id
        return link.id, data

    def _serialize_highlight(self, highlight) -> typing.Tuple[str, typing.Dict]:
        links = self._serialize_entities(highlight.links, self._serialize_link) if highlight.links else {}
        backlinks = self._serialize_entities(highlight.backlinks, self._serialize_backlink)
        return highlight.id, {
            "location": highlight.location,
            "links": links,
            "backlinks": backlinks,
            "content": highlight.note.body if highlight.note else None,
        }


class DocumentRepositoryDocument(Document):

    def _repository_init(self, version: int, content_id: lib.Id):
        self.content_id = content_id
        self.version = version


class DocumentRepositoryLink(Link):
    # keep known data directly on link to avoid having to load a ref

    def _repository_init(self, source_document_id, source_workspace, target_document_id, target_workspace,
                         source_highlight_id=None, target_highlight_id=None):
        self.source_document_id = source_document_id
        self.source_workspace = source_workspace
        self.source_highlight_id = source_highlight_id
        self.target_document_id = target_document_id
        self.target_workspace = target_workspace
        self.target_highlight_id = target_highlight_id


class DocumentModifiedByOtherUser(ValueError):
    pass
