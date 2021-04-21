import typing
import abc
from domain import lib
from . import Workspace, Document


class DocumentRepository(lib.Repository):

    @abc.abstractmethod
    def get(self, id_: lib.Id, workspace: Workspace) -> Document:
        pass

    @abc.abstractmethod
    def add(self, document: Document):
        pass

    @abc.abstractmethod
    def get_all_in_workspace(self, workspace: Workspace) -> typing.List[Document]:
        pass
