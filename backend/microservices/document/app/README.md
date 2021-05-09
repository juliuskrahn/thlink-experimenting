# App

## Structure

- controllers
- interface (interface of the controllers to the outside world)
- middleware (between the controllers and the outside world - error handling)
- chef (utility for controllers)
- implementation (domain extension, see Domain Implementation)
- notification (events - other services can subscribe to)
- repository

## Domain Implementation

The application extends the core domain with the following rules:
    - There are 3 content-types: "pdf", "web-page", and "thlink-document"
    - "thlink-document" content is "living"; only "living" content can be updated
    - Only entities with non "living" content can be highlighted; a highlight is layered on top of content
    - A link on "living" content is placed inside the content
    - Updating "living" content updates links; they can't be created/ deleted independently
    - A link on non "living" content is layered on top of the content
    - The content-type of a highlight note is always "thlink-document"
    - The parent of a highlight is always a document
