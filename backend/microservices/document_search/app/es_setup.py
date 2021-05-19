from elasticsearch_dsl import Index, Document as EsDocument, Text, Object, analyzer

document_index = Index('DocumentV1')

document_index.settings(
    number_of_shards=4,
    number_of_replicas=1,
)

document_index.aliases(Document={})


@document_index.document
class Document(EsDocument):
    title = Text()


# You can attach custom analyzers to the index # TODO ?
html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

document_index.analyzer(html_strip)

document_index.create()
