import abc
import uuid


class Id(str):

    def __init__(self, value: str = None):
        if value is None:
            value = uuid.uuid4()
        super().__init__(value)


class Entity(abc.ABC):

    def __init__(self, id_: Id):
        self._id = id_

    @property
    def id(self):
        return self._id

    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    @property
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