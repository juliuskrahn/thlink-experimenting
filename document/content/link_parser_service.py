from .content import Content


class ContentLinkParserService:

    def parse(self, content: Content):
        assert content.is_md()
        return []
