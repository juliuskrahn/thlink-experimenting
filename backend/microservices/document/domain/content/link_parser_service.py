from .content import Content
import typing


class ContentLinkParserService:

    def parse(self, content: Content) -> typing.List[str]:
        assert content.is_md()
        return []
