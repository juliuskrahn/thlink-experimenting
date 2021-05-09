# TODO test events


def test_can_create_document(lambda_context, MockedMiddlewareWithoutErrorCatching):
    from app.controllers.document_create.lambda_function import handler
    event = {
        "workspace": "MyWorkspace",
        "title": "MyDocument",
        "tags": ["Important"],
        "contentType": "pdf",
        "contentBody": "Lorem ipsum",
        "links": [],
        "highlights": [],
    }
    response = handler(event.copy(), lambda_context)

    assert type(response.get("id")) == str
    assert response.get("contentBodyUrl") == "url"
    assert response.get("version") == 1
    for attribute in event:
        if attribute != "contentBody":
            assert response[attribute] == event[attribute]


def test_can_create_document_with_links(lambda_context, controller_other_created_document,
                                        MockedMiddlewareWithoutErrorCatching):
    from app.controllers.document_create.lambda_function import handler
    event = {
        "workspace": "MyWorkspace",
        "title": "MyDocument",
        "tags": ["Important"],
        "contentType": "pdf",
        "contentBody": "Lorem ipsum",
        "links": [
            {
                "location": "6:15",
                "targetDocumentId": controller_other_created_document["id"],
            }
        ],
        "highlights": [],
    }
    response = handler(event.copy(), lambda_context)

    assert type(response["links"][0].get("id")) == str
    for attribute in event:
        if attribute != "links" and attribute != "contentBody":
            assert response[attribute] == event[attribute]
    for attribute in event["links"][0]:
        assert response["links"][0][attribute] == event["links"][0][attribute]


def test_can_delete_document(lambda_context, controller_other_created_document,
                             MockedMiddlewareWithoutErrorCatching):
    from app.controllers.document_delete.lambda_function import handler
    event = {
        "workspace": controller_other_created_document["workspace"],
        "documentId": controller_other_created_document["id"],
    }
    response = handler(event.copy(), lambda_context)

    assert response["documentId"] == controller_other_created_document["id"]
    assert response["workspace"] == controller_other_created_document["workspace"]


def test_can_get_document(lambda_context, controller_other_created_document,
                          MockedMiddlewareWithoutErrorCatching):
    from app.controllers.document_get.lambda_function import handler
    event = {
        "workspace": controller_other_created_document["workspace"],
        "documentId": controller_other_created_document["id"],
    }
    response = handler(event.copy(), lambda_context)

    assert response == controller_other_created_document


def test_can_get_all_documents_in_workspace(lambda_context,
                                            controller_created_document, controller_other_created_document,
                                            MockedMiddlewareWithoutErrorCatching):
    from app.controllers.document_get_all_in_workspace.lambda_function import handler
    event = {
        "workspace": controller_created_document["workspace"],
    }
    response = handler(event.copy(), lambda_context)

    # response does not contain document content bodies

    controller_created_document["contentBodyUrl"] = None
    assert controller_created_document in response["documents"]

    controller_other_created_document["contentBodyUrl"] = None
    assert controller_other_created_document in response["documents"]


def test_can_create_document_highlight(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                       controller_created_document):
    from app.controllers.document_highlight_create.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "location": "6:15",
        "linkPreviewText": "Lorem",
    }
    response = handler(event.copy(), lambda_context)

    assert type(response["highlights"][0].get("id")) == str
    for attribute in controller_created_document:
        if attribute != "highlights" and attribute != "contentBodyUrl":
            assert controller_created_document[attribute] == response[attribute]
    assert event["location"] == response["highlights"][0]["location"]
    assert event["linkPreviewText"] == response["highlights"][0]["linkPreviewText"]


def test_can_create_document_highlight_with_note_and_links(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                                           controller_created_document,
                                                           controller_other_created_document):
    from app.controllers.document_highlight_create.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "location": "6:15",
        "linkPreviewText": "Lorem",
        "noteBody": "Lorem",
        "links": [{
            "location": "1:4",
            "targetDocumentId": controller_other_created_document["id"],
        }],
    }
    response = handler(event.copy(), lambda_context)

    assert type(response["highlights"][0].get("id")) == str
    assert type(response["highlights"][0]["links"][0].get("id")) == str
    for attribute in controller_created_document:
        if attribute != "highlights" and attribute != "contentBodyUrl":
            assert controller_created_document[attribute] == response[attribute]
    assert event["location"] == response["highlights"][0]["location"]
    assert event["linkPreviewText"] == response["highlights"][0]["linkPreviewText"]
    assert event["noteBody"] == response["highlights"][0]["noteBody"]
    assert event["links"][0]["location"] == response["highlights"][0]["links"][0]["location"]
    assert event["links"][0]["targetDocumentId"] == response["highlights"][0]["links"][0]["targetDocumentId"]


def test_can_delete_document_highlight(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                       controller_created_document, controller_created_document_highlight_id):
    from app.controllers.document_highlight_delete.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "documentHighlightId": controller_created_document_highlight_id,
    }
    response = handler(event.copy(), lambda_context)

    controller_created_document["contentBodyUrl"] = None
    assert controller_created_document == response


def test_can_create_document_highlight_note(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                            controller_created_document, controller_other_created_document,
                                            controller_created_document_highlight_id):
    from app.controllers.document_highlight_note.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "documentHighlightId": controller_created_document_highlight_id,
        "linkPreviewText": "Lorem",
        "noteBody": "Lorem",
        "links": [{
            "location": "1:4",
            "targetDocumentId": controller_other_created_document["id"],
        }],
    }
    response = handler(event.copy(), lambda_context)

    assert type(response["highlights"][0]["links"][0].get("id")) == str
    for attribute in controller_created_document:
        if attribute != "highlights" and attribute != "contentBodyUrl":
            assert controller_created_document[attribute] == response[attribute]
    assert event["linkPreviewText"] == response["highlights"][0]["linkPreviewText"]
    assert event["noteBody"] == response["highlights"][0]["noteBody"]
    assert event["links"][0]["location"] == response["highlights"][0]["links"][0]["location"]
    assert event["links"][0]["targetDocumentId"] == response["highlights"][0]["links"][0]["targetDocumentId"]


def test_can_delete_document_highlight_note(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                            controller_created_document, controller_created_document_highlight_id):
    from app.controllers.document_highlight_note.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": controller_created_document["workspace"],
        "documentHighlightId": controller_created_document_highlight_id,
        "linkPreviewText": "Lorem",
        "noteBody": None,
        "links": None,
    }
    response = handler(event.copy(), lambda_context)

    for attribute in controller_created_document:
        if attribute != "highlights" and attribute != "contentBodyUrl":
            assert controller_created_document[attribute] == response[attribute]
    assert not response["highlights"][0].get("noteBody")
    assert not response["highlights"][0].get("links")


def test_can_create_document_link(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                  controller_created_document, controller_other_created_document):
    from app.controllers.document_link_create.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "location": "6:15",
        "targetDocumentId": controller_other_created_document["id"],
    }
    response = handler(event.copy(), lambda_context)

    assert type(response["links"][0].get("id")) == str
    for attribute in controller_created_document:
        if attribute != "links" and attribute != "contentBodyUrl":
            assert controller_created_document[attribute] == response[attribute]
    assert event["targetDocumentId"] == response["links"][0]["targetDocumentId"]
    assert event["location"] == response["links"][0]["location"]


# TODO link highlight


def test_can_delete_document_link(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                  controller_created_document, controller_other_created_document):
    from app.controllers.document_link_create.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "location": "6:15",
        "targetDocumentId": controller_other_created_document["id"],
    }
    response = handler(event.copy(), lambda_context)
    link_id = response["links"][0].get("id")

    from app.controllers.document_link_delete.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "documentLinkId": link_id,
    }
    response = handler(event.copy(), lambda_context)

    controller_created_document["contentBodyUrl"] = None
    assert controller_created_document == response


# TODO link highlight


def test_can_rename_document(lambda_context, MockedMiddlewareWithoutErrorCatching, controller_created_document):
    from app.controllers.document_rename.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "title": "NewTitle",
    }
    response = handler(event.copy(), lambda_context)

    controller_created_document["contentBodyUrl"] = None
    controller_created_document["title"] = event["title"]
    assert controller_created_document == response


def test_can_add_tag_to_document(lambda_context, MockedMiddlewareWithoutErrorCatching, controller_created_document):
    from app.controllers.document_tag_add.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "tag": "NewTag",
    }
    response = handler(event.copy(), lambda_context)

    controller_created_document["contentBodyUrl"] = None
    controller_created_document["tags"].append(event["tag"])
    assert controller_created_document == response


def test_can_remove_tag_from_document(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                      controller_created_document):
    from app.controllers.document_tag_add.lambda_function import handler
    event = {
        "documentId": controller_created_document["id"],
        "workspace": "MyWorkspace",
        "tag": "NewTag",
    }
    response = handler(event.copy(), lambda_context)

    from app.controllers.document_tag_remove.lambda_function import handler
    response = handler(event.copy(), lambda_context)

    controller_created_document["contentBodyUrl"] = None
    assert response == controller_created_document


def test_can_update_document_content(lambda_context, MockedMiddlewareWithoutErrorCatching,
                                     controller_created_document_with_living_content):
    from app.controllers.document_update_content.lambda_function import handler
    event = {
        "documentId": controller_created_document_with_living_content["id"],
        "workspace": "MyWorkspace",
        "contentBody": "Lorem novum ipsum",
    }
    response = handler(event.copy(), lambda_context)

    controller_created_document_with_living_content["version"] += 1
    assert response == controller_created_document_with_living_content


# TODO update content + links
