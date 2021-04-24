from __future__ import annotations
import typing
from copy import deepcopy
import functools
from domain import lib
from domain.model.document.link import LinkPreview
from domain.model.document import Document, Workspace, Link, Highlight, Content, ContentLocation
from domain.model.document import DocumentRepository as AbstractDocumentRepository
from .db import DB, ItemKey
from .object_storage import ObjectStorage


class DocumentRepository(AbstractDocumentRepository):

    def __init__(self):
        documents_type = typing.Dict[[lib.Id, Workspace]: Document]
        self._documents: documents_type = {}
        self._documents_loaded: documents_type = {}
        self._db = DB()
        self._object_storage = ObjectStorage()
        self._document_factory = DocumentFactory(self, self._object_storage)

    def get(self, id_: lib.Id, workspace: Workspace) -> Document:
        document = self._documents.get((id_, workspace))
        if document:
            return document
        raw_document = self._db.get_item(ItemKey("workspace", workspace, secondary=ItemKey("id", id_)))
        document = self._document_factory.build_document(raw_document)
        self._documents[(document.id, document.workspace)] = document
        self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return document

    def add(self, document: Document):
        self._documents[(document.id, document.workspace)] = document

    def get_all_in_workspace(self, workspace: Workspace) -> typing.List[Document]:  # TODO handle fragmentation
        raw_documents = self._db.query_items(ItemKey("workspace", workspace))
        documents = []
        for raw_document in raw_documents:
            document = self._document_factory.build_document(raw_document)
            documents.append(document)
            self._documents[(document.id, document.workspace)] = document
            self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return documents

    def _save(self):
        for document in set(self._collect_dirty_documents()):
            self._save_document(document)

    def _save_document(self, document: Document):
        document_loaded = self._documents_loaded.get((document.id, document.workspace))
        if document.deleted:
            if document_loaded:
                self._db.delete(ItemKey("workspace", document.workspace, secondary=ItemKey("id", document.id)))
        elif document_loaded and document_loaded.content == document.content:
            self._db.update(
                key=ItemKey("workspace", document.workspace, secondary=ItemKey("id", document.id)),
                item=DocumentSerializer.serialize_document(document),
                old_item=DocumentSerializer.serialize_document(document_loaded),
            )
        else:
            self._db.put(item=DocumentSerializer.serialize_document(document))

    def _document_is_dirty(self, document: Document):
        return DocumentSerializer.serialize_document(self._documents_loaded.get((document.id, document.workspace))) \
               != DocumentSerializer.serialize_document(document)

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

    def __init__(self, document_repository: DocumentRepository, object_storage: ObjectStorage):
        self._document_repository = document_repository
        self._object_storage = object_storage
        fragments_type = typing.Dict[[lib.Id, Workspace, lib.Id]: Document]
        self._fragment_links: fragments_type = {}
        self._fragment_link_previews: fragments_type = {}

    def build_document(self, data: typing.Dict) -> Document:
        id_ = lib.Id(data["id"])
        workspace = Workspace(data["workspace"])
        link_preview = self._get_link_preview_for_document(id_, workspace, lambda: LinkPreview(data["title"], None))
        content = Content(
            body=self._cached_property(lambda: self._object_storage.get(data["content"]["id"])),
            type=data["content"]["type"],
        )

        def link(link_id: lib.Id, link_data) -> Link:
            def factory():
                def node_ref_info(node_ref_data):
                    node_highlight_id = node_ref_data.get("highlight_id")
                    if node_highlight_id:
                        node_highlight_id = lib.Id(node_highlight_id)
                        node_link_preview = self._get_link_preview_for_document_highlight(
                            id_,
                            workspace,
                            node_highlight_id,
                            lambda: LinkPreview(node_ref_data["link_preview"], link_preview),
                        )
                    else:
                        node_link_preview = self._get_link_preview_for_document(
                            id_,
                            workspace,
                            lambda: LinkPreview(node_ref_data["link_preview"], None)
                        )
                    node_ref_property = self._node_ref_property(lib.Id(node_ref_data["id"]),
                                                                Workspace(node_ref_data["workspace"]),
                                                                node_highlight_id)
                    return node_ref_property, node_link_preview

                source, source_link_preview = node_ref_info(link_data["source"])
                target, target_link_preview = node_ref_info(link_data["target"])

                return Link(
                    id_=link_id,
                    location=ContentLocation(link_data["location"]),
                    source=source,
                    source_link_preview=source_link_preview,
                    target=target,
                    target_link_preview=target_link_preview,
                )

            return self._get_link(link_id, factory)

        def highlight(highlight_id: lib.Id, highlight_data) -> Highlight:
            highlight_links = [link(lib.Id(raw_link_id), link_data) for raw_link_id, link_data
                               in highlight_data["links"].items()]
            highlight_backlinks = [link(lib.Id(raw_link_id), link_data) for raw_link_id, link_data
                                   in highlight_data["backlinks"].items()]

            return Highlight(
                id_=highlight_id,
                location=ContentLocation(highlight_data["location"]),
                parent=self._node_ref_property(id_, workspace),
                link_preview=self._get_link_preview_for_document_highlight(id_, workspace, highlight_id,
                                                                           lambda: highlight_data["content"]["body"]),
                links=highlight_links,
                backlinks=highlight_backlinks,
                note=highlight_data["note"],
            )

        links = [link(lib.Id(raw_link_id), link_data) for raw_link_id, link_data in data["links"].items()]
        backlinks = [link(lib.Id(raw_link_id), link_data) for raw_link_id, link_data in data["backlinks"].items()]
        highlights = [highlight(lib.Id(raw_highlight_id), highlight_data) for raw_highlight_id, highlight_data
                      in data["highlights"].items()]

        return Document(
            id_=id_,
            workspace=workspace,
            title=data["title"],
            link_preview=link_preview,
            tags=data["tags"],
            content=content,
            links=links,
            backlinks=backlinks,
            highlights=highlights,
        )

    def _get_link(self, id_: lib.Id, factory_fn: typing.Callable):
        link = self._fragment_links.get(id_)
        if link:
            return link
        link = factory_fn()
        self._fragment_links[id_] = link
        return link

    def _get_link_preview_for_document(self, id_: lib.Id, workspace: Workspace, factory_fn: typing.Callable):
        link_preview = self._fragment_link_previews.get((id_, workspace))
        if not link_preview:
            link_preview = factory_fn()
            self._fragment_link_previews[(id_, workspace)] = link_preview
        return link_preview

    def _get_link_preview_for_document_highlight(self, document_id: lib.Id, workspace: Workspace, highlight_id: lib.Id,
                                                 factory_fn: typing.Callable):
        link_preview = self._fragment_link_previews.get((document_id, workspace, highlight_id))
        if not link_preview:
            link_preview = factory_fn()
            self._fragment_link_previews[(document_id, workspace, highlight_id)] = link_preview
        return link_preview

    @staticmethod
    def _cached_property(getter: typing.Callable):
        return property(functools.cache(lambda _: getter()))

    def _node_ref_property(self, id_: lib.Id, workspace: Workspace, highlight_id: lib.Id = None):
        @property
        @functools.cache
        def ref_property(_):
            document = self._document_repository.get(id_, workspace)
            if highlight_id:
                return document.get_highlight(highlight_id)
            return document
        return ref_property


class DocumentSerializer:

    @staticmethod
    def serialize_document(document: Document) -> typing.Dict:
        def serialize_link(link):
            pass

        links = [serialize_link()]
        backlinks = [serialize_link()]

        def serialize_highlight(highlight):
            pass

        highlights = [serialize_highlight()]

        return {
            "id": document.id,
            "workspace": document.workspace,
            "title": document.title,
            "tags": [*document.tags],
            "links": links,
            "backlinks": backlinks,
            "highlights": highlights,
        }
