from __future__ import annotations
import typing
import abc
import contextlib


class Repository(abc.ABC):

    @abc.abstractmethod
    def _save(self):
        pass

    @classmethod
    @abc.abstractmethod
    @contextlib.contextmanager
    def use(cls) -> typing.ContextManager[Repository]:
        # yield repository
        # call _save
        pass
