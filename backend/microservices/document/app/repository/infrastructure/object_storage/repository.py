from .object_storage import ObjectStorage


class DocumentRepositoryObjectStorage(ObjectStorage):

    def __init__(self):
        super().__init__("DocumentContent")
