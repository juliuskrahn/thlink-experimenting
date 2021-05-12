import os
from uuid import uuid4
import boto3
import botocore.exceptions
from app.interface import DocumentModel, DocumentIdentifierModel


class NotificationManager:

    def __init__(self):
        sns = boto3.resource("sns")
        document_event_sns_topic_arn = os.environ.get("DocumentEventSNSTopicARN")
        self._document_event_sns_topic = sns.Topic(document_event_sns_topic_arn)

    def _publish(self, event_type: str, event_message_json_str: str, group_id: str):
        try:
            response = self._document_event_sns_topic.publish(
                Message=event_message_json_str,
                MessageDeduplicationId=uuid4().hex,
                MessageGroupId=group_id,
                MessageAttributes={"eventType": event_type},
            )
        except botocore.exceptions.ClientError as e:
            raise InternalError() from e

    def document_saved(self, document_model: DocumentModel):
        self._publish("documentSaved", document_model.json(), group_id=document_model.id)

    def document_deleted(self, document_identifier_model: DocumentIdentifierModel):
        self._publish("documentDeleted", document_identifier_model.json(),
                      group_id=document_identifier_model.document_id)


class InternalError(Exception):
    pass
