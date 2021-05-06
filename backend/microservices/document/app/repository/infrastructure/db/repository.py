from .db import DB


class DocumentRepositoryDB(DB):

    def __init__(self):
        super().__init__("Document")
