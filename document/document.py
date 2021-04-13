from .content import Content, ContentContainer
from .links import Links
from .highlights import Highlights, DocumentHighlightsPolicy
import typing


class Document(ContentContainer):

    def __init__(self,
                 id_: str,
                 title: str,
                 tags: typing.List[str],
                 living: bool,
                 content: Content,
                 links: typing.Optional[Links],
                 backlinks,
                 highlights: typing.Optional[Highlights],
                 ):
        self._id = id_
        self.title = title
        self.tags = tags
        self._living = living
        self._content = content
        if not living:
            self.highlights = highlights
        super().__init__(
            content,
            Links.from_content(self.content) if living else links,
            backlinks,
        )

        assert LivingDocumentPolicy.is_satisfied_by(self)
        assert DocumentHighlightsPolicy.is_satisfied_by(self)

    @property
    def living(self):
        return self._living


class LivingDocumentPolicy:

    @staticmethod
    def is_satisfied_by(document: Document):
        return not document.living or document.content.is_md()
