import enum


class ContentType(enum.Enum):
    MD = "MD"
    PDF = "PDF"
    HTML = "HTML"


class Content:

    def __init__(self, value, content_type: ContentType):
        self.value = value
        self._type = ContentType[content_type]
    
    @property
    def type(self):
        return self._type

    def is_md(self):
        return self._type == ContentType.MD

    def is_pdf(self):
        return self._type == ContentType.PDF

    def is_html(self):
        return self._type == ContentType.HTML
