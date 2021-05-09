import boto3
import botocore.exceptions


class ObjectStorage:

    def __init__(self, name: str):
        self._client = boto3.client("s3")
        self._bucket = name

    def get(self, id_: str):
        try:
            resp = self._client.get_object(
                Bucket=self._bucket,
                Key=id_,
            )
            return resp["Body"]
        except botocore.exceptions.ClientError as e:
            raise

    def get_url(self, id_: str):
        pass  # TODO

    def put(self, id_: str, body):
        try:
            resp = self._client.put_object(
                Bucket=self._bucket,
                Key=id_,
                Body=body,
            )
        except botocore.exceptions.ClientError as e:
            raise

    def delete(self, id_: str):
        try:
            resp = self._client.delete_object(Bucket=self._bucket, Key=id_)
        except botocore.exceptions.ClientError as e:
            raise
