from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain.model.document import Document, Workspace, Content
from app.repository import DocumentRepository
from app.implementation import ContentTypePolicy
from app.interface import PreparedDocumentModel, DocumentModel
from app.chef import DocumentChef
from app.middleware import middleware, BadOperationUserError
from app.notification import NotificationManager


class Event(PreparedDocumentModel):
    pass


class Response(DocumentModel):
    pass


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    if not ContentTypePolicy.is_satisfied_by(event.content_type):
        raise BadOperationUserError("Invalid content type")

    workspace = Workspace(event.workspace)
    content = Content(event.content_body, event.content_type)

    notification_manager = NotificationManager()

    with DocumentRepository.use() as repository:
        links = DocumentChef(repository).prepare_links(workspace, event.links) if event.links else []
        document = Document.create(
            workspace,
            event.title,
            event.tags,
            content,
            links,
            highlights=[],
        )
        repository.add(document)

        def on_saved_document(saved_document):
            if saved_document.id == document.id:
                model = Response.build(saved_document, with_content_body_url=True)
            else:
                model = Response.build(saved_document)
            notification_manager.document_saved(model)

        repository.on_saved_document = on_saved_document

    response = Response.build(document, with_content_body_url=True)
    return response.dict()
