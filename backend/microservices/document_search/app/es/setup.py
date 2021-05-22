from elasticsearch_dsl import Index, Document, InnerDoc, Nested, Text, Integer
from . import client


app_document_search_index = Index('DocumentSearchV1', using=client)

app_document_search_index.settings(
    number_of_shards=4,
    number_of_replicas=1,
)

app_document_search_index.aliases(Document={})


class AppHighlight(InnerDoc):
    # id is the highlight id
    link_preview_text = Text()
    backlinks_count = Integer()


@app_document_search_index.document
class AppDocument(Document):
    # id is the document id
    workspace = Text()
    title = Text()
    tag = Text()
    backlinks_count = Integer()  # + the sum of the backlinks_count of all contained highlights
    highlights = Nested(AppHighlight)
    content_type = Text()
    # TODO content body


def setup():
    app_document_search_index.create()
