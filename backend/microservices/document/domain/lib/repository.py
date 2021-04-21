import abc
import contextlib


class Repository(abc.ABC):

    @abc.abstractmethod
    def _save(self):
        pass

    @classmethod
    @contextlib.contextmanager
    def use(cls):
        repository = cls()
        yield repository
        repository._save()
