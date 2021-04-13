from . import Document
from .content import Content, ContentContainer
from .links import Linkable, Links
import typing


class BaseHighlight:

    def __init__(self, id_: str):
        self._id = id_

    @property
    def id(self):
        return self._id


class Highlight(BaseHighlight, Linkable):

    def __init__(self, id_: str, backlinks):
        super().__init__(id_)
        super(BaseHighlight, self).__init__(backlinks)

    def to_note(self):
        pass


class Note(BaseHighlight, ContentContainer):

    def __init__(self, id_: str, backlinks, content: Content):
        super().__init__(id_)
        super(BaseHighlight, self).__init__(
            content,
            Links.from_content(content),
            backlinks
        )

        assert NoteContentPolicy.is_satisfied_by(self)

    def to_highlight(self):
        pass


class Highlights(dict):

    def __init__(self, list_: typing.List[BaseHighlight]):
        super().__init__()
        for highlight in list_:
            self[highlight.id] = highlight


class DocumentHighlightsPolicy:

    @staticmethod
    def is_satisfied_by(document: Document):
        if hasattr(document, "highlights"):
            return not document.living
        return document.living


class NoteContentPolicy:

    @staticmethod
    def is_satisfied_by(note: Note):
        return note.content.is_md()
