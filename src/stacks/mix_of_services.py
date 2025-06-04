from aws_cdk import App, Duration, Stack
from aws_cdk import aws_athena as athena
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subs
from aws_cdk import aws_sqs as sqs


class VariousServicesExampleStack(Stack):
    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SQS Queue
        sqs.Queue(
            self,
            "ExampleQueue",
            visibility_timeout=Duration.seconds(300),
        )

        # SNS Topic
        topic = sns.Topic(self, "ExampleTopic")

        # SNS Subscription
        subscription = subs.EmailSubscription("example@example.com")
        topic.add_subscription(subscription)

        # IAM Managed Policy
        iam.ManagedPolicy(
            self,
            "ExampleManagedPolicy",
            statements=[
                iam.PolicyStatement(actions=["s3:ListBucket"], resources=["*"])
            ],
        )

        # Athena Workgroup
        athena.CfnWorkGroup(
            self,
            "ExampleWorkgroup",
            name="example_workgroup",
            state="ENABLED",
            work_group_configuration={
                "enforceWorkGroupConfiguration": True,
                "publishCloudWatchMetricsEnabled": True,
                "requesterPaysEnabled": False,
            },
        )

        # added as part of article EC2 Key Pair
        ec2.CfnKeyPair(
            self,
            "ExampleKeyPair",
            key_name="example-key-pair",
            key_type="rsa",
            public_key_material="ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAr...example",
        )
