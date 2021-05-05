from __future__ import annotations
from typing import List, Generator, ContextManager, Dict, Callable, Union, Tuple
from copy import deepcopy
from domain import lib
from domain.model.document.link import LinkPreview
from domain.model.document import Document, Workspace, Link, Highlight, Content, ContentLocation
from domain.model.document import DocumentRepository as AbstractDocumentRepository
from .infrastructure import db, object_storage
from .document import DocumentRepositoryDocument
from .document_serialization import SerializedDocument, SerializedLink, SerializedBacklink, SerializedHighlight,\
    DocumentSerializer
from app.implementation import THLINK_DOCUMENT


class DocumentRepository(AbstractDocumentRepository):

    def __init__(self):
        self._documents: Dict[Tuple[lib.Id, Workspace], DocumentRepositoryDocument] = {}
        self._documents_loaded: Dict[Tuple[lib.Id, Workspace], DocumentRepositoryDocument] = {}
        self._db = db.DB()
        self._object_storage = object_storage.ObjectStorage()
        self._document_factory = DocumentFactory(self)
        self._document_serializer = DocumentSerializer()

    @classmethod
    def use(cls) -> ContextManager[DocumentRepository]:
        repository = cls()
        yield repository
        repository._save()

    def get(self, document_id: lib.Id, workspace: Workspace) -> DocumentRepositoryDocument:
        document = self._documents.get((document_id, workspace))
        if document:
            return document
        if self._document_factory.document_id == document_id:
            raise RecursionError("Attempted to get a document that is currently being build")
        db_item = self._db.get_item(db.ItemKey("workspace", workspace, secondary=db.ItemKey("id", document_id)))
        document = self._document_factory.build_document(
            SerializedDocument(**db_item),
            content_body_getter=lambda content_id: self._object_storage.get(content_id),
        )
        self._documents[(document.id, document.workspace)] = document
        self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return document

    def get_all_in_workspace(self, workspace: Workspace) -> List[DocumentRepositoryDocument]:
        for document in self._documents_loaded:
            if document.workspace == workspace:
                assert ValueError("Workspace is already partially loaded")
        db_items = self._db.query_items(db.ItemKey("workspace", workspace))
        documents = []
        for db_item in db_items:
            document = self._document_factory.build_document(
                SerializedDocument(**db_item),
                content_body_getter=lambda content_id: lambda: self._object_storage.get(content_id),
            )
            documents.append(document)
            self._documents[(document.id, document.workspace)] = document
            self._documents_loaded[(document.id, document.workspace)] = deepcopy(document)
        return documents

    def add(self, document: Document):
        self._documents[(document.id, document.workspace)] = document
        DocumentRepositoryDocument._repository_init(document, version=0, content_id=lib.Id())

    def _save(self):
        for document in set(self._collect_dirty_documents()):  # deduplicate
            self._save_document(document)

    def _save_document(self, document: DocumentRepositoryDocument):
        document_loaded = self._documents_loaded.get((document.id, document.workspace))
        if document.deleted:
            if document_loaded:
                self._db.delete(db.ItemKey("workspace", document.workspace, secondary=db.ItemKey("id", document.id)))
                self._object_storage.delete(document.content_id.value)
        elif document_loaded and document_loaded.content == document.content:
            self._db.update(
                key=db.ItemKey("workspace", document.workspace, secondary=db.ItemKey("id", document.id)),
                item=self._document_serializer.serialize_document(document),
                old_item=self._document_serializer.serialize_document(document_loaded),
            )
        else:
            document.version += 1
            try:
                self._db.put(
                    key=db.ItemKey("workspace", document.workspace, secondary=db.ItemKey("id", document.id)),
                    item=self._document_serializer.serialize_document(document),
                    expect_if_item_exists={"version": document.version - 1}
                )
            except db.ExpectationNotMet:
                raise DocumentContentUpdatedByOtherUserError
            self._object_storage.put(document.content_id.value, document.content.body)
            # TODO Saga Pattern

    def _document_is_dirty(self, document: DocumentRepositoryDocument):
        document_loaded = self._documents_loaded.get((document.id, document.workspace))

        def document_mutated():
            return self._document_serializer.serialize_document(document_loaded) \
                   != self._document_serializer.serialize_document(document)

        return not document_loaded or document_mutated()

    def _collect_dirty_documents(self) -> Generator[DocumentRepositoryDocument]:
        # May yield duplicates
        for document in self._documents.values():
            if self._document_is_dirty(document):
                for indirect in self._collect_indirect_dirty_documents(document):
                    yield indirect
                yield document

    def _collect_indirect_dirty_documents(self, document: DocumentRepositoryDocument) \
            -> Generator[DocumentRepositoryDocument]:
        # Causes for indirect dirty documents are link preview changes on entities that are referenced by other entities
        # which might not be loaded.

        document_loaded = self._documents_loaded.get((document.id, document.workspace))
        if not document_loaded:
            # all changes must have been registered by referencing entities - so they are already known to be dirty
            raise StopIteration

        document_link_targets_are_dirty = document_loaded.link_preview != document.link_preview

        if document_link_targets_are_dirty:
            for link in document.links:
                yield link.target

        def highlight_link_targets_are_dirty(highlight: Highlight):
            loaded_highlight = document_loaded.get_highlight(highlight.id)
            return loaded_highlight and loaded_highlight.links \
                and loaded_highlight.link_preview != highlight.link_preview

        for document_highlight in document.highlights:
            if highlight_link_targets_are_dirty(document_highlight):
                for link in document_highlight.links:
                    yield link.target


class DocumentFactory:

    def __init__(self, document_repository: DocumentRepository):
        self._document_repository = document_repository

        # Links and LinkPreviews are referenced by multiple entities that are instantiated independently,
        # this means we have to reuse already instantiated Links/ LinkPreviews.
        self._links: Dict[lib.Id, Link] = {}  # key -> link id
        self._link_previews: Dict[lib.Id, LinkPreview] = {}  # key -> document id/ document highlight id

        # Store the id of the document that is currently being build so that the document repository can prevent
        # bootstrapping loops
        self._document_id = None

    def build_document(self, serialized: SerializedDocument, content_body_getter: Callable)\
            -> DocumentRepositoryDocument:
        document_id = lib.Id(serialized.id)
        self._document_id = document_id
        workspace = Workspace(serialized.workspace)
        content_id = lib.Id(serialized.content_id)
        document_link_preview = self._get_link_preview(
            id_=document_id,
            factory_fn=lambda: LinkPreview(serialized.title, None),
        )
        content = lib.Lazy(lambda: Content(
            body=content_body_getter(content_id),
            type=serialized.content_type,
        ), known_properties={"type": serialized.content_type})

        lazy_document = lib.Lazy(
            getter=lambda: self._document_repository.get(document_id, workspace),
            known_properties={
                "id": document_id,
                "workspace": workspace,
                "link_preview": document_link_preview,
            },
        )

        links = [self._get_link(ser_link_id, serialized.links[ser_link_id], lazy_document)
                 for ser_link_id in serialized.links]
        backlinks = [self._get_link(ser_link_id, serialized.backlinks[ser_link_id], lazy_document)
                     for ser_link_id in serialized.backlinks]
        highlights = [self._get_highlight(ser_highlight_id, serialized.highlights[ser_highlight_id], lazy_document)
                      for ser_highlight_id in serialized.highlights]

        document = DocumentRepositoryDocument(
            id_=document_id,
            workspace=workspace,
            title=serialized.title,
            link_preview=document_link_preview,
            tags=serialized.tags,
            content=content,
            links=links,
            backlinks=backlinks,
            highlights=highlights,
        )
        document._repository_init(serialized.version, content_id)
        self._document_id = None
        return document

    def _get_link(self,
                  serialized_id: str,
                  serialized: Union[SerializedLink, SerializedBacklink],
                  scope: Union[Document, Highlight],
                  ):
        link_id = lib.Id(serialized_id)
        link = self._links.get(link_id)
        if link:
            return link

        across_is_target = as_link = isinstance(serialized, SerializedLink)

        def get_across() -> Union[Document, Highlight]:
            if across_is_target:
                across_document_id = lib.Id(serialized.target_document_id)
                across_document_highlight_id = serialized.target_document_highlight_id
            else:
                across_document_id = lib.Id(serialized.source_document_id)
                across_document_highlight_id = serialized.source_document_highlight_id

            across_is_of_type_highlight = bool(across_document_highlight_id)

            # link preview

            if across_is_of_type_highlight:
                across_document_highlight_id = lib.Id(across_document_highlight_id)
                across_link_preview = self._get_link_preview(
                    id_=across_document_highlight_id,
                    factory_fn=lambda:
                        LinkPreview(
                            text=serialized.target_document_highlight_preview_text if across_is_target
                            else serialized.source_document_highlight_preview_text,
                            parent=self._get_link_preview(
                                id_=across_document_id,
                                factory_fn=lambda: LinkPreview(
                                    text=serialized.target_document_preview_text if across_is_target
                                    else serialized.source_document_preview_text,
                                    parent=None),
                            ),
                        ),
                )

            else:
                across_link_preview = self._get_link_preview(
                    id_=across_document_id,
                    factory_fn=lambda: LinkPreview(
                        text=serialized.target_document_preview_text if across_is_target
                        else serialized.source_document_preview_text,
                        parent=None),
                )

            # lazy across Document/ Highlight

            across_known_properties = {
                "link_preview": across_link_preview,
            }

            if across_is_of_type_highlight:
                across_known_properties["id"] = across_document_highlight_id
                across_known_properties["parent"] = lib.Lazy(
                    getter=lambda: self._document_repository.get(across_document_id, scope.workspace),
                    known_properties={"id": across_document_id, "workspace": scope.workspace},
                )

                def getter():
                    return self._document_repository.get(across_document_id, scope.workspace)\
                        .get_highlight(across_document_highlight_id)

            else:
                across_known_properties["id"] = across_document_id,
                across_known_properties["workspace"] = scope.workspace

                def getter():
                    return self._document_repository.get(across_document_id, scope.workspace)

            return lib.Lazy(getter=getter, known_properties=across_known_properties)

        across = get_across()

        link = Link(
            id_=link_id,
            location=ContentLocation(serialized.location),
            source=scope if across_is_target else across,
            source_link_preview=scope.link_preview if across_is_target else across.link_preview,
            target=across if across_is_target else scope,
            target_link_preview=across.link_preview if across_is_target else scope.link_preview,
        )

        self._links[link_id] = link
        return link

    def _get_link_preview(self, id_: lib.Id, factory_fn: Callable):
        link_preview = self._link_previews.get(id_)
        if not link_preview:
            link_preview = factory_fn()
            self._link_previews[id_] = link_preview
        return link_preview

    def _get_highlight(self, scope: Document, serialized_id: str, serialized: SerializedHighlight) -> Highlight:
        highlight_id = lib.Id(serialized_id)
        highlight_link_preview = self._get_link_preview(
            id_=highlight_id,
            factory_fn=lambda: LinkPreview(text=serialized.link_preview_text, parent=scope.link_preview)
        )
        lazy_highlight = lib.Lazy(
            getter=lambda: scope.get_highlight(highlight_id),
            known_properties={"id": highlight_id, "parent": scope, "link_preview": highlight_link_preview}
        )
        links = [self._get_link(ser_link_id, serialized.links[ser_link_id], lazy_highlight)
                 for ser_link_id in serialized.links]
        backlinks = [self._get_link(ser_link_id, serialized.backlinks[ser_link_id], lazy_highlight)
                     for ser_link_id in serialized.backlinks]
        return Highlight(
            id_=highlight_id,
            location=ContentLocation(serialized.location),
            parent=scope,
            link_preview=highlight_link_preview,
            links=links,
            backlinks=backlinks,
            note=Content(body=serialized.note_body, type=THLINK_DOCUMENT) if serialized.note_body else None,
        )

    @property
    def document_id(self):
        return self._document_id


class DocumentContentUpdatedByOtherUserError(ValueError):
    pass
