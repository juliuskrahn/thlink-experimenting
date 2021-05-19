from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import SearchEventModel, EsDocumentModel
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MatchPhrasePrefix
from app.es_client import get_es_client


@event_parser(model=SearchEventModel)
def handler(event: SearchEventModel, context: LambdaContext):
    client = get_es_client()

    s = Search(using=client, index="my-index")\
        .filter("workspace", workspaces=[event.workspace])\
        .query(MatchPhrasePrefix(
            query=event.query,
            fields=[
                "title^4",
                "tags^3",
                "contentBody^1",
            ],

        ))\

    response = s.execute()
    for hit in response:
        pass
