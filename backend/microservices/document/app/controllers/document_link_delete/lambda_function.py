from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain import lib
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.implementation import LivingContentTypePolicy
from app.interface import SourceDocumentLinkIdentifierModel, DocumentModel


class Event(SourceDocumentLinkIdentifierModel):
    pass


class Response(DocumentModel):
    pass


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    document_id = lib.Id(event.document_id)
    workspace = Workspace(event.workspace)
    document_link_id = lib.Id(event.document_link_id)

    with DocumentRepository.use() as repository:
        document = repository.get(document_id, workspace)
        assert not LivingContentTypePolicy.is_satisfied_by(document.content.type)
        document.get_link(document_link_id).delete()

    return dict(Response.build(document))
