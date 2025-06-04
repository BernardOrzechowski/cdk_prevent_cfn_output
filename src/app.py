import os

import aws_cdk as cdk
from stacks.stack_bucket_import import StackImportingBucket
from stacks.stack_with_bucket import StackWithBucketExport

app = cdk.App()

stack_with_bucket_export = StackWithBucketExport(
    app,
    "StackWithBucketExport",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

stack_importing_bucket = StackImportingBucket(
    app,
    "StackImportingBucket",
    imported_bucket=stack_with_bucket_export.bucket,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
