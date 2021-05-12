import pytest
from dataclasses import dataclass
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from app.repository.infrastructure import db, object_storage
from tests.app.mocks.repository_infrastructure.db import DocumentRepositoryDB
from tests.app.mocks.repository_infrastructure.object_storage import DocumentRepositoryObjectStorage
import app.notification
from tests.app.mocks.notification import NotificationManager
from domain.model.document import Document, Content, ContentLocation, Workspace
from app import middleware


@pytest.fixture(autouse=True)
def MockedDBForDocumentRepository(monkeypatch):
    DocumentRepositoryDB._table = {}
    DocumentRepositoryDB.count_query_operations = 0
    DocumentRepositoryDB.count_get_operations = 0
    DocumentRepositoryDB.count_put_operations = 0
    DocumentRepositoryDB.count_update_operations = 0
    DocumentRepositoryDB.count_delete_operations = 0
    monkeypatch.setattr(db, "DocumentRepositoryDB", DocumentRepositoryDB)
    return DocumentRepositoryDB


@pytest.fixture(autouse=True)
def MockedObjectStorageForDocumentRepository(monkeypatch):
    DocumentRepositoryObjectStorage._storage = {}
    DocumentRepositoryObjectStorage.count_get_operations = 0
    DocumentRepositoryObjectStorage.count_get_url_operations = 0
    DocumentRepositoryObjectStorage.count_put_operations = 0
    DocumentRepositoryObjectStorage.count_delete_operations = 0
    monkeypatch.setattr(object_storage, "DocumentRepositoryObjectStorage", DocumentRepositoryObjectStorage)
    return DocumentRepositoryObjectStorage


@pytest.fixture
def MockedMiddlewareWithoutErrorCatching(monkeypatch):
    @lambda_handler_decorator
    def middleware_without_error_catching(handler, event, context):
        response = handler(event, context)
        return response
    monkeypatch.setattr(middleware, "middleware", middleware_without_error_catching)


@pytest.fixture(autouse=True)
def MockedEvent(monkeypatch):
    monkeypatch.setattr(app.notification, "NotificationManager", NotificationManager)


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"
    return LambdaContext()


@pytest.fixture
def content():
    return Content("Lorem [[ipsum]]", "MD")


@pytest.fixture
def content_location():
    return ContentLocation("6:15")


@pytest.fixture
def workspace():
    return Workspace("MyWorkspace")


@pytest.fixture
def other_workspace():
    return Workspace("MyOtherWorkspace")


@pytest.fixture
def document(content, workspace):
    return Document.create(workspace, "MyDocument",
                           tags=["Important"], content=content, links=[], highlights=[])


@pytest.fixture
def other_document(content, workspace):
    return Document.create(workspace, "MyOtherDocument",
                           tags=["Other"], content=content, links=[], highlights=[])


@pytest.fixture
def document_from_other_workspace(content, other_workspace):
    return Document.create(other_workspace, "MyDocumentFromAnotherWorkspace",
                           tags=[], content=content, links=[], highlights=[])


@pytest.fixture
def controller_created_document(lambda_context):
    from app.controllers.document_create.lambda_function import handler
    event = {
        "workspace": "MyWorkspace",
        "title": "MyDocument",
        "tags": ["Important"],
        "contentType": "pdf",
        "contentBody": "Lorem ipsum",
        "links": [],
        "highlights": [],
    }
    return handler(event.copy(), lambda_context)


@pytest.fixture
def controller_other_created_document(lambda_context):
    from app.controllers.document_create.lambda_function import handler
    event = {
        "workspace": "MyWorkspace",
        "title": "MyOtherDocument",
        "tags": ["Other"],
        "contentType": "pdf",
        "contentBody": "Lorem ipsum",
        "links": [],
        "highlights": [],
    }
    return handler(event.copy(), lambda_context)


@pytest.fixture
def controller_created_document_highlight_id(lambda_context, controller_created_document):
    from app.controllers.document_highlight_create.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "location": "6:15",
        "linkPreviewText": "Lorem",
    }
    response = handler(event.copy(), lambda_context)
    return response["highlights"][0]["id"]


@pytest.fixture
def controller_created_document_with_living_content(lambda_context):
    from app.controllers.document_create.lambda_function import handler
    event = {
        "workspace": "MyWorkspace",
        "title": "MyDocument",
        "tags": ["Important"],
        "contentType": "thlink-document",
        "contentBody": "Lorem ipsum",
        "links": [],
        "highlights": [],
    }
    return handler(event.copy(), lambda_context)
