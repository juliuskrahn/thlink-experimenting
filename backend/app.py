from aws_cdk import core

from backend.microservices.document.app.stack import DocumentServiceStack
from backend.microservices.document_search.app.stack import DocumentSearchServiceStack

app = core.App()

document_service_stack = DocumentServiceStack(app, "DocumentService")
document_search_service_stack = DocumentSearchServiceStack(app, "DocumentSearchService", document_service_stack)

app.synth()
