import os
import botocore.exceptions
import boto3
from app.interface import DocumentModel, DocumentIdentifierModel


class EventManager:

    def __init__(self):
        sns = boto3.resource("sns")
        document_event_sns_topic_arn = os.environ.get("DocumentEventSNSTopicARN")
        self._document_event_sns_topic = sns.Topic(document_event_sns_topic_arn)

    def _publish(self, event_type: str, event_message_json_str: str, group_id: str):
        try:
            response = self._document_event_sns_topic.publish(
                Message=event_message_json_str,
                MessageGroupId=group_id,
                MessageAttributes={"eventType": event_type},
            )
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def document_created(self, document: DocumentModel):
        self._publish("documentCreated", document.json(by_alias=True), group_id=document.id)

    def document_mutated(self, document: DocumentModel):
        self._publish("documentMutated", document.json(by_alias=True), group_id=document.id)

    def document_deleted(self, identifier: DocumentIdentifierModel):
        self._publish("documentDeleted", identifier.json(by_alias=True), group_id=identifier.document_id)


class InternalError(Exception):
    pass
