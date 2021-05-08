from typing import Dict, Any, Tuple, Optional
from app.repository.infrastructure.db import ItemKey, ExpectationNotMet


class DocumentRepositoryDB:

    _table: Dict[Tuple[str, Optional[str]], Any]

    count_query_operations: int

    def query_items(self, key: ItemKey):
        DocumentRepositoryDB.count_query_operations += 1
        items = []
        for found_key, found_item in DocumentRepositoryDB._table.items():
            if found_key[0] == key.value:
                items.append(found_item)
        return items

    count_get_operations: int

    def get_item(self, key: ItemKey, count=True):
        if count:
            DocumentRepositoryDB.count_get_operations += 1
        return DocumentRepositoryDB._table.get(self._key_for_table(key))

    count_put_operations: int

    def put(self, key: ItemKey, item: Dict, expect_if_item_exists: Dict = None, count=True):
        if expect_if_item_exists is None:
            expect_if_item_exists = {}
        if count:
            DocumentRepositoryDB.count_put_operations += 1
        assert key.name in item
        assert not key.secondary or key.secondary.name in item
        existing = self.get_item(key, count=False)
        if existing:
            for name, value in expect_if_item_exists.values():
                if existing.get(name) != value:
                    raise ExpectationNotMet()
        DocumentRepositoryDB._table[self._key_for_table(key)] = item

    count_update_operations: int

    def update(self, key: ItemKey, item: Dict, old_item: Dict):
        DocumentRepositoryDB.count_update_operations += 1
        self.put(key, item, count=False)

    count_delete_operations: int

    def delete(self, key: ItemKey):
        DocumentRepositoryDB.count_delete_operations += 1
        if self._key_for_table(key) in self._table:
            del DocumentRepositoryDB._table[self._key_for_table(key)]

    @staticmethod
    def test_operations_count(query=0, get=0, put=0, update=0, delete=0):
        assert DocumentRepositoryDB.count_query_operations == query
        assert DocumentRepositoryDB.count_get_operations == get
        assert DocumentRepositoryDB.count_put_operations == put
        assert DocumentRepositoryDB.count_update_operations == update
        assert DocumentRepositoryDB.count_delete_operations == delete

    @staticmethod
    def _key_for_table(key: ItemKey):
        if key.secondary:
            return key.value, key.secondary.value
        return key.value, None
