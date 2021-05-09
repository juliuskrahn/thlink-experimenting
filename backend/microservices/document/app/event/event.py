import os
import botocore.exceptions
import boto3
from app.interface import DocumentModel, DocumentIdentifierModel


sns = boto3.resource("sns")

document_event_sns_topic_arn = os.environ.get("DocumentEventSNSTopicARN")

document_event_sns_topic = sns.Topic(document_event_sns_topic_arn)


def _publish(event_type: str, event_message_json_str: str, group_id: str):
    try:
        response = document_event_sns_topic.publish(
            Message=event_message_json_str,
            MessageGroupId=group_id,
            MessageAttributes={"eventType": event_type},
        )
    except botocore.exceptions.ClientError as e:
        raise FailedToPublishEvent() from e


def document_created(document: DocumentModel):
    _publish("documentCreated", document.json(by_alias=True), group_id=document.id)


def document_mutated(document: DocumentModel):
    _publish("documentMutated", document.json(by_alias=True), group_id=document.id)


def document_deleted(identifier: DocumentIdentifierModel):
    _publish("documentDeleted", identifier.json(by_alias=True), group_id=identifier.document_id)


class FailedToPublishEvent(Exception):
    pass
