from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain.model.document import Document, Workspace, Content
from app.repository import DocumentRepository
from app.implementation import ContentTypePolicy
from app.interface import PreparedDocumentModel, DocumentModel
from app.utils import prepare_links, prepare_highlights


class Event(PreparedDocumentModel):
    pass


class Response(DocumentModel):
    pass


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    assert ContentTypePolicy.is_satisfied_by(event.content_type),\
        f"Content Type must be one of {ContentTypePolicy.types}."

    workspace = Workspace(event.workspace)
    content = Content(event.content_body, event.content_type)

    with DocumentRepository.use() as repository:
        links = prepare_links(repository, workspace, event.links) if event.links else []
        highlights = prepare_highlights(repository, workspace, event.highlights) if event.highlights else []

        document = Document.create(
            workspace,
            event.title,
            event.tags,
            content,
            links,
            highlights,
        )

        repository.add(document)

    return dict(Response.build(document, with_content_body=True))
