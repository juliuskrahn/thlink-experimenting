PDF = "pdf"
WEB_PAGE = "web-page"
THLINK_DOCUMENT = "thlink-document"


class ContentTypePolicy:

    types = [PDF, WEB_PAGE, THLINK_DOCUMENT]

    @classmethod
    def is_satisfied_by(cls, content_type: str):
        return content_type in cls.types


class LivingContentTypePolicy:

    types = [THLINK_DOCUMENT]

    @classmethod
    def is_satisfied_by(cls, content_type: str):
        return content_type in cls.types
