from app.interface import DocumentModel, DocumentIdentifierModel


class EventManager:

    def document_created(self, document: DocumentModel):
        pass

    def document_mutated(self, document: DocumentModel):
        pass

    def document_deleted(self, identifier: DocumentIdentifierModel):
        pass
