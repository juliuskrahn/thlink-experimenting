from app.interface import DocumentModel
from domain.model.document import Link


def test_document_model(document, other_document, content_location, content):
    backlink = other_document.link(content_location, document)
    link = document.link(content_location, other_document)
    highlight = document.highlight(content_location, link_preview_text=content.body)
    highlight_link = Link.prepare(content_location, other_document)
    highlight_backlink = other_document.link(content_location, highlight)
    highlight.make_note(content, links=[highlight_link])
    build_dict = DocumentModel.build(document, with_content_body=True).dict(by_alias=True)

    assert build_dict == {
        "id": str(document.id),
        "title": document.title,
        "workspace": str(document.workspace),
        "tags": document.tags,
        "contentBody": document.content.body,
        "contentType": document.content.type,
        "links": [{
            "id": str(link.id),
            "location": str(link.location),
            "targetDocumentId": str(other_document.id),
            "targetDocumentHighlightId": None,
            "targetDocumentPreviewText": other_document.link_preview.text,
            "targetDocumentHighlightPreviewText": None,
        }],
        "backlinks": [{
            "id": str(backlink.id),
            "location": str(backlink.location),
            "sourceDocumentId": str(other_document.id),
            "sourceDocumentHighlightId": None,
            "sourceDocumentPreviewText": other_document.link_preview.text,
            "sourceDocumentHighlightPreviewText": None,
        }],
        "highlights": [{
            "id": str(highlight.id),
            "location": str(highlight.location),
            "noteBody": highlight.note.body,
            "linkPreviewText": str(highlight.link_preview.text),
            "links": [{
                "id": str(highlight_link.id),
                "location": str(highlight_link.location),
                "targetDocumentId": str(other_document.id),
                "targetDocumentHighlightId": None,
                "targetDocumentPreviewText": other_document.link_preview.text,
                "targetDocumentHighlightPreviewText": None,
            }],
            "backlinks": [{
                "id": str(highlight_backlink.id),
                "location": str(highlight_backlink.location),
                "sourceDocumentId": str(other_document.id),
                "sourceDocumentHighlightId": None,
                "sourceDocumentPreviewText": other_document.link_preview.text,
                "sourceDocumentHighlightPreviewText": None,
            }],
        }],
    }
