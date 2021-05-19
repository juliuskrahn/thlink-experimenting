from aws_cdk import core
import aws_cdk.aws_elasticsearch as es
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subs


class DocumentSearchServiceStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, document_service_stack, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        es_domain = es.Domain(
            self,
            "DocumentSearch",
            domain_name="DocumentSearch",
            capacity=es.CapacityConfig(
                data_node_instance_type="t3.small.elasticsearch",
                data_nodes=1,  # at least 3 for multi-AZ
            ),
            ebs=es.EbsOptions(
                volume_type="gp2",
                volume_size=10,
            ),
            zone_awareness=es.ZoneAwarenessConfig(
                enabled=False,  # switch to enable multi-AZ
                availability_zone_count=3,
            ),
            logging=es.LoggingOptions(),
            removal_policy=core.RemovalPolicy.RETAIN,
            version=es.ElasticsearchVersion.V7_10,
            enable_version_upgrade=True,
        )

        document_event_sns_topic: sns.Topic = document_service_stack.document_event_sns_topic
        self.update_on_document_event_lambda_function = lambda_.Function()
        document_event_sns_topic.add_subscription(subs.LambdaSubscription(
            self.update_on_document_event_lambda_function)
        )
        es_domain.grant_write(self.update_on_document_event_lambda_function)
