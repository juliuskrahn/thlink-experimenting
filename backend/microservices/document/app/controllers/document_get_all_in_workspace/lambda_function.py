from typing import List
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from domain.model.document import Workspace
from app.repository import DocumentRepository
from app.interface import BaseModel, WorkspaceIdentifierModel, DocumentModel


class Event(WorkspaceIdentifierModel):
    pass


class Response(BaseModel):
    documents: List[DocumentModel]


@event_parser(model=Event)
def handler(event: Event, context: LambdaContext):
    workspace = Workspace(event.workspace)

    with DocumentRepository.use() as repository:
        documents = repository.get_all_in_workspace(workspace)

    return dict(Response(documents=[DocumentModel.build(document) for document in documents]))
