from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import SearchEventModel, SearchResponseModel, SearchResponseDocumentModel,\
    SearchResponseHighlightModel
from elasticsearch_dsl.query import Bool, Nested, MultiMatch
from app.es import AppDocument


@event_parser(model=SearchEventModel)
def handler(event: SearchEventModel, context: LambdaContext):
    # TODO boost based on backlink count
    #  https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html

    match_document = MultiMatch(
        query=event.query,
        fields=[
            "title",
            "tag^2",
            "content_type"
        ],
    )
    match_highlight = Nested(
        query=MultiMatch(
            query=event.query,
            fields=[
                "link_preview_text",
            ],
        ),
        path="highlights",
        score_mode="max",
        nested_inner_hits={
            "size": 8,
        },
    )
    s = AppDocument.search()\
        .filter("workspace", workspace=event.workspace)\
        .query(Bool(must=[match_document, match_highlight]))

    response = s.execute()

    documents = []
    for hit in response:
        highlights = []
        if hit.inner_hits:
            for inner_hit in hit.inner_hits:
                highlights.append(SearchResponseHighlightModel(
                    id=inner_hit.id,
                    link_preview_text=inner_hit.link_preview_text,
                ))
        documents.append(SearchResponseDocumentModel(
            workspace=hit.workspace,
            id=hit.id,
            title=hit.title,
            tags=hit.tag if type(hit.tag) is list else [hit.tag],
            highlights=highlights,
            content_type=hit.content_type,
        ))
    return SearchResponseModel(documents=documents).dict()
