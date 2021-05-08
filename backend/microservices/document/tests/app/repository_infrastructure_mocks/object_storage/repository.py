from typing import Dict, Any


class DocumentRepositoryObjectStorage:

    _storage: Dict[str, Any]

    count_get_operations: int

    def get(self, id_: str):
        DocumentRepositoryObjectStorage.count_get_operations += 1
        return DocumentRepositoryObjectStorage._storage.get(id_)

    count_put_operations: int

    def put(self, id_: str, body):
        DocumentRepositoryObjectStorage.count_put_operations += 1
        DocumentRepositoryObjectStorage._storage[id_] = body

    count_delete_operations: int

    def delete(self, id_: str):
        DocumentRepositoryObjectStorage.count_delete_operations += 1
        if id_ in DocumentRepositoryObjectStorage._storage:
            del DocumentRepositoryObjectStorage._storage[id_]

    @staticmethod
    def test_operations_count(get=0, put=0, delete=0):
        assert DocumentRepositoryObjectStorage.count_get_operations == get
        assert DocumentRepositoryObjectStorage.count_put_operations == put
        assert DocumentRepositoryObjectStorage.count_delete_operations == delete
