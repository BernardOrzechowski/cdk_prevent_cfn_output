import aws_cdk as cdk
import aws_cdk.aws_s3 as s3

from stacks.cfn_output_validator import StackValidator


class StackImportingBucket(cdk.Stack):
    def __init__(
        self, scope: cdk.App, construct_id: str, imported_bucket: s3.Bucket, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "MyFirstBucket",
            bucket_name=f"{imported_bucket.bucket_name}_2",
            versioned=True,
        )

        self.node.add_validation(StackValidator(stack=self))
