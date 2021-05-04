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

    def __hash__(self):
        return hash(self.value)

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

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"{self.__class__}({self._info()})"


class RootEntity(Entity):
    """
    Life cycle:
    - create
      /init (instantiate)
    - mutate; behaviour creates child entities
    - delete; delete child entities
    """

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass


class ChildEntity(Entity):
    """
    Life cycle:
    - create
        prepare (pass data)
        primary parent -> behaviour (pass itself) -> completes child entity (-> registers on all parents)
      /init (instantiate)
    - mutate
    - delete
        (-> unregisters on all parents)
    """

    @classmethod
    @abc.abstractmethod
    def prepare(cls, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _complete(self, primary_parent: RootEntity):
        # called by primary parent
        pass

    @property
    @abc.abstractmethod
    def completed(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass


class ChildEntityManager:

    def __init__(self, list_: typing.List[Entity]):
        self._dict = {entity.id: entity for entity in list_}

    def get_all(self) -> typing.ValuesView:
        return self._dict.values()

    def get(self, id_: Id):
        return self._dict[id_]

    def register(self, entity: Entity):
        self._dict[entity.id] = entity

    def unregister(self, id_: Id):
        del self._dict[id_]
