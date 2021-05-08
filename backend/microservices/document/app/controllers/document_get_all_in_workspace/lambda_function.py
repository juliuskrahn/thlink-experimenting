from typing import List
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import BaseModel, WorkspaceIdentifierModel, DocumentModel
from app.middleware import middleware


class Event(WorkspaceIdentifierModel):
    pass


class Response(BaseModel):
    documents: List[DocumentModel]


@middleware
@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        documents = repository.get_all_in_workspace(workspace)

    return Response(documents=[DocumentModel.build(document) for document in documents]).dict(by_alias=True)
