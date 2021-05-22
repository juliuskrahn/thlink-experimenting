from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from app.interface import DocumentSavedEventModel
from app.es import AppDocument, AppHighlight


@event_parser(model=DocumentSavedEventModel)
def handler(event: DocumentSavedEventModel, context: LambdaContext):
    highlights = []
    all_highlights_backlinks_count = 0
    for highlight in event.highlights:
        backlinks_count = len(highlight.backlinks)
        all_highlights_backlinks_count += backlinks_count
        highlights.append(AppHighlight(
            link_preview_text=highlight.link_preview_text,
            backlinks_count=backlinks_count,
        ))
    document = AppDocument(
        workspace=event.workspace,
        title=event.title,
        tag=event.tags,
        backlinks_count=len(event.backlinks) + all_highlights_backlinks_count,
        higlights=highlights,
        content_type=event.content_type,
    )
    document.save()
