import typing
import abc
import uuid


class Id:

    def __init__(self, value: str = None):
        if value is None:
            value = uuid.uuid4().hex
        self._value = value

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return self.value


class Entity(abc.ABC):

    def __init__(self, id_: Id):
        self._id = id_

    @property
    def id(self):
        return self._id

    @abc.abstractmethod
    def delete(self):
        pass

    @property
    @abc.abstractmethod
    def deleted(self):
        pass

    @abc.abstractmethod
    def _info(self) -> str:
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.__class__}({self._info()})"


class ChildEntities:

    def __init__(self, list_: typing.List[Entity]):
        self._dict = {entity.id: entity for entity in list_}

    def view(self) -> typing.ValuesView:
        return self._dict.values()

    def get(self, id_: Id):
        return self._dict[id_]

    def register(self, entity: Entity):
        self._dict[entity.id] = entity

    def unregister(self, id_: Id):
        del self._dict[id_]
