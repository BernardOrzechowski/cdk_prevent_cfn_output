#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.mix_of_services import VariousServicesExampleStack
from stacks.storage import StorageStack

# from hello_cdk.hello_cdk_stack import (
#     StackImportingBucket,  # noqa: E501
#     StackWithBucketExport,
# )

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

storage_stack = StorageStack(
    app,
    "StorageStack",
    env=env,
)

example_services_stack = VariousServicesExampleStack(
    app,
    "VariousServicesExampleStack",
    env=env,
)


app.synth()
