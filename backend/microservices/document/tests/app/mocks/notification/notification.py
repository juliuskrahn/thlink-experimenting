from app.interface import DocumentModel, DocumentIdentifierModel


class NotificationManager:

    def document_saved(self, document_model: DocumentModel):
        pass

    def document_deleted(self, identifier_model: DocumentIdentifierModel):
        pass
