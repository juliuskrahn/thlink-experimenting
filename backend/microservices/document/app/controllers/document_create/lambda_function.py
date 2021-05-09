from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain.model.document import Document, Workspace, Content
from app.repository import DocumentRepository
from app.implementation import ContentTypePolicy
from app.interface import PreparedDocumentModel, DocumentModel
from app.utils import prepare_links
from app.middleware import middleware, BadOperationUserError
import app.event


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

    with DocumentRepository.use() as repository:
        links = prepare_links(repository, workspace, event.links) if event.links else []

        document = Document.create(
            workspace,
            event.title,
            event.tags,
            content,
            links,
            highlights=[],
        )

        repository.add(document)

    response = Response.build(document, with_content_body_url=True)
    app.event.document_created(response)
    return response.dict(by_alias=True)
