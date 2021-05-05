from domain import lib
from domain.model.document import Document


class DocumentRepositoryDocument(Document):

    content_id: lib.Id
    version: int

    def _repository_init(self: Document, version: int, content_id: lib.Id):
        self.content_id = content_id
        self.version = version
