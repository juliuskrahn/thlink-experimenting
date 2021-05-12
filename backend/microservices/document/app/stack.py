from typing import List
import os
import shutil
import subprocess
from aws_cdk import core
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_sns as sns
import aws_cdk.aws_logs as logs


class DocumentServiceStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        build()

        self.document_event_sns_topic = sns.Topic(
            self,
            "DocumentEvent",
            topic_name="DocumentEvent",
            display_name="Document Event Topic",
            fifo=True,
        )

        document_dynamodb_table = dynamodb.Table(
            self,
            "Document",
            table_name="Document",
            partition_key=dynamodb.Attribute(name="workspace", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
        )

        document_content_s3_bucket = s3.Bucket(
            self,
            "DocumentContent",
            bucket_name="DocumentContent",
            removal_policy=core.RemovalPolicy.RETAIN,
        )

        controller_lambda_layers = [
            lambda_.LayerVersion(
                self,
                "App",
                code=lambda_.Code.from_asset("_build/app_layer"),
                compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            ),
            lambda_.LayerVersion(
                self,
                "AWSLambdaPowertools",
                code=lambda_.Code.from_asset("_build/aws_lambda_powertools_layer"),
                compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            ),
        ]

        self.document_create_lambda_function = ControllerLambdaFunction(
            self,
            "document_create",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_create_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_create_lambda_function)
        document_content_s3_bucket.grant_write(self.document_create_lambda_function)

        self.document_delete_lambda_function = ControllerLambdaFunction(
            self,
            "document_delete",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_delete_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_delete_lambda_function)
        document_content_s3_bucket.grant_delete(self.document_delete_lambda_function)

        self.document_get_lambda_function = ControllerLambdaFunction(
            self,
            "document_get",
            layers=controller_lambda_layers,
        )
        document_dynamodb_table.grant_read_data(self.document_get_lambda_function)
        document_content_s3_bucket.grant_read(self.document_get_lambda_function)

        self.document_get_all_in_workspace_lambda_function = ControllerLambdaFunction(
            self,
            "document_get_all_in_workspace",
            layers=controller_lambda_layers,
        )
        document_dynamodb_table.grant_read_data(self.document_get_all_in_workspace_lambda_function)

        self.document_highlight_create_lambda_function = ControllerLambdaFunction(
            self,
            "document_highlight_create",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_highlight_create_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_highlight_create_lambda_function)

        self.document_highlight_delete_lambda_function = ControllerLambdaFunction(
            self,
            "document_highlight_delete",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_highlight_delete_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_highlight_delete_lambda_function)

        self.document_highlight_note_lambda_function = ControllerLambdaFunction(
            self,
            "document_highlight_note",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_highlight_note_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_highlight_note_lambda_function)

        self.document_link_create_lambda_function = ControllerLambdaFunction(
            self,
            "document_link_create",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_link_create_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_link_create_lambda_function)

        self.document_link_delete_lambda_function = ControllerLambdaFunction(
            self,
            "document_link_delete",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_link_delete_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_link_delete_lambda_function)

        self.document_rename_lambda_function = ControllerLambdaFunction(
            self,
            "document_rename",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_rename_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_rename_lambda_function)

        self.document_tag_add_lambda_function = ControllerLambdaFunction(
            self,
            "document_tag_add",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_tag_add_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_tag_add_lambda_function)

        self.document_tag_remove_lambda_function = ControllerLambdaFunction(
            self,
            "document_tag_remove",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_tag_remove_lambda_function)
        document_dynamodb_table.grant_read_write_data(self.document_tag_remove_lambda_function)

        self.document_update_content_function = ControllerLambdaFunction(
            self,
            "document_update_content",
            layers=controller_lambda_layers,
        )
        self.document_event_sns_topic.grant_publish(self.document_update_content_function)
        document_dynamodb_table.grant_read_write_data(self.document_update_content_function)
        document_content_s3_bucket.grant_write(self.document_update_content_function)


class ControllerLambdaFunction(lambda_.Function):

    def __init__(self, scope: DocumentServiceStack, controller_name: str, layers: List[lambda_.LayerVersion]):
        super().__init__(
            scope,
            id=to_camel_case(controller_name),
            code=lambda_.Code.from_asset(f"controllers/{controller_name}"),
            handler="lambda_function.handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment={
                "DocumentEventSNSTopicARN": scope.document_event_sns_topic.topic_arn,
            },
            memory_size=256,
            layers=layers,
            log_retention=logs.RetentionDays.FIVE_DAYS,
        )


def build():
    shutil.rmtree("_build", ignore_errors=True)
    os.mkdir("_build")

    # app layer
    os.makedirs("_build/app_layer/python")
    shutil.copytree("../app", "_build/app_layer/python",
                    ignore=lambda src, names: ["controllers", "stack.py", "README.md"])
    shutil.copytree("../domain", "_build/app_layer/python")

    # aws lambda powertools layer
    os.makedirs("_build/lambda_powertools_layer/python")
    subprocess.run(["pip", "install", "aws_lambda_powertools", "-t", "_build/lambda_powertools_layer/python"])


def to_camel_case(string: str):
    """Returns a CamelCase version of the string and removes some characters"""
    string = string.title()
    remove = ["_", " ", ".", "-", ":", "@", "#", "!", "?", "(", ")", "[", "]", "{", "}", "/", "\\", ",", "=", ">", "<",
              "|"]
    string = string.translate({ord(c): None for c in remove})
    return string
