from app.repository import DocumentRepository
from app import interface
from domain.model.document import Link


def test_save_and_retrieve_document_with_content(document,
                                                 MockedDBForDocumentRepository,
                                                 MockedObjectStorageForDocumentRepository,
                                                 ):
    with DocumentRepository.use() as repository:
        repository.add(document)

    with DocumentRepository.use() as repository:
        retrieved_document = repository.get(document.id, document.workspace)

    assert interface.DocumentModel.build(document=document, with_content_body=True) \
           == interface.DocumentModel.build(document=retrieved_document, with_content_body=True)

    MockedDBForDocumentRepository.test_operations_count(put=1, get=1)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=1, get=1)


def test_save_and_retrieve_all_documents_in_workspace(document, other_document, document_from_other_workspace,
                                                      MockedDBForDocumentRepository,
                                                      MockedObjectStorageForDocumentRepository,
                                                      ):
    with DocumentRepository.use() as repository:
        repository.add(document)
        repository.add(other_document)
        repository.add(document_from_other_workspace)

    with DocumentRepository.use() as repository:
        retrieved_documents = repository.get_all_in_workspace(document.workspace)

    assert len(retrieved_documents) == 2
    for retrieved_document in retrieved_documents:
        if retrieved_document.id == document.id:
            assert interface.DocumentModel.build(document=document) \
                   == interface.DocumentModel.build(document=retrieved_document)
        elif retrieved_document.id == other_document.id:
            assert interface.DocumentModel.build(document=other_document) \
                   == interface.DocumentModel.build(document=retrieved_document)
        else:
            assert None

    MockedDBForDocumentRepository.test_operations_count(put=3, query=1)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=3, get=0)


def test_save_and_retrieve_document_with_link(document, other_document, content_location,
                                              MockedDBForDocumentRepository,
                                              MockedObjectStorageForDocumentRepository,
                                              ):
    with DocumentRepository.use() as repository:
        repository.add(other_document)
        repository.add(document)
        link = document.link(content_location, other_document)

    with DocumentRepository.use() as repository:
        retrieved_document = repository.get(document.id, document.workspace)

    retrieved_document_link = retrieved_document.get_link(link.id)

    assert interface.DocumentModel.build(document=document) \
           == interface.DocumentModel.build(document=retrieved_document)
    assert retrieved_document_link.target.id == other_document.id

    MockedDBForDocumentRepository.test_operations_count(get=1, put=2)

    # will result in a db get
    assert retrieved_document_link.target.get_backlink(retrieved_document_link.id) == retrieved_document_link

    MockedDBForDocumentRepository.test_operations_count(get=2, put=2)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=2, get=0)


def test_save_and_retrieve_document_with_highlight_with_link(document, other_document, content_location, content,
                                                             MockedDBForDocumentRepository,
                                                             MockedObjectStorageForDocumentRepository,
                                                             ):
    with DocumentRepository.use() as repository:
        repository.add(other_document)
        repository.add(document)
        highlight = document.highlight(content_location, link_preview_text=content.body)
        highlight_link = Link.prepare(content_location, other_document)
        highlight.make_note(content, links=[highlight_link])

    with DocumentRepository.use() as repository:
        retrieved_document = repository.get(document.id, document.workspace)

    retrieved_document_highlight_link = retrieved_document.get_highlight(highlight.id).get_link(highlight_link.id)

    assert interface.DocumentModel.build(document=document) \
           == interface.DocumentModel.build(document=retrieved_document)
    assert retrieved_document_highlight_link.target.id == other_document.id

    MockedDBForDocumentRepository.test_operations_count(get=1, put=2)

    # will result in a db get
    assert retrieved_document_highlight_link.target.get_backlink(retrieved_document_highlight_link.id) \
           == retrieved_document_highlight_link

    MockedDBForDocumentRepository.test_operations_count(get=2, put=2)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=2, get=0)


def test_save_and_retrieve_document_with_backlink(document, other_document, content_location,
                                                  MockedDBForDocumentRepository,
                                                  MockedObjectStorageForDocumentRepository,
                                                  ):
    with DocumentRepository.use() as repository:
        repository.add(other_document)
        repository.add(document)
        backlink = other_document.link(content_location, document)

    with DocumentRepository.use() as repository:
        retrieved_document = repository.get(document.id, document.workspace)

    retrieved_document_backlink = retrieved_document.get_backlink(backlink.id)

    assert interface.DocumentModel.build(document=document) \
           == interface.DocumentModel.build(document=retrieved_document)
    assert retrieved_document_backlink.source.id == other_document.id

    MockedDBForDocumentRepository.test_operations_count(get=1, put=2)

    # will result in a db get
    assert retrieved_document_backlink.source.get_link(retrieved_document_backlink.id) == retrieved_document_backlink

    MockedDBForDocumentRepository.test_operations_count(get=2, put=2)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=2, get=0)


def test_save_and_retrieve_document_with_highlight_with_backlink(document, other_document, content_location, content,
                                                                 MockedDBForDocumentRepository,
                                                                 MockedObjectStorageForDocumentRepository,
                                                                 ):
    with DocumentRepository.use() as repository:
        repository.add(other_document)
        repository.add(document)
        highlight = document.highlight(content_location, link_preview_text=content.body)
        highlight_backlink = other_document.link(content_location, highlight)

    with DocumentRepository.use() as repository:
        retrieved_document = repository.get(document.id, document.workspace)

    retrieved_document_highlight_backlink = retrieved_document.get_highlight(highlight.id)\
        .get_backlink(highlight_backlink.id)

    assert interface.DocumentModel.build(document=document) \
           == interface.DocumentModel.build(document=retrieved_document)
    assert retrieved_document_highlight_backlink.source.id == other_document.id

    MockedDBForDocumentRepository.test_operations_count(get=1, put=2)

    # will result in a db get
    assert retrieved_document_highlight_backlink.source.get_link(retrieved_document_highlight_backlink.id) \
           == retrieved_document_highlight_backlink

    MockedDBForDocumentRepository.test_operations_count(get=2, put=2)
    MockedObjectStorageForDocumentRepository.test_operations_count(put=2, get=0)
