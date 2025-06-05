
# How to prevent cross tack dependencies in CDK Applications?

AWS CDK has a set of [best practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html) that serve as a guide to efficient use of CDK. There is also a set of [best practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html) for Cloud Formation. As your CDK code will always end up as a set of Cloud Formation templates you need to consider both for optimal setup. 

The problem is that some of these best practices are questionable and based on my teams extensive experience with large CDK code base - there are better approaches for some. 

I described in this article [CDK / Cloud Formation — do not follow blindly all best practices!](https://medium.com/qoob-dev/cdk-cloud-formation-do-not-follow-blindly-all-best-practices-c529464c8e9d) how to avoid using cross stack references.

You will encounter the situation where you need to use a resource (name or ARN or some other property) defined in other stack.
The AWS recommended way is to use cross stack references implemented in Cloud Formation as `Outputs` section (generator side) and `Fn::ImportValue` section (receiver side). But there are huge disadvantages to this approach.

What we want to avoid is such an object in generated Cloud Formation template (`Outputs` section):

```json
{
 "Resources": {
  "MyFirstBucketB8884501": {
   "Type": "AWS::S3::Bucket",
   "Properties": {
    "VersioningConfiguration": {
     "Status": "Enabled"
    }
   },
 ....
 "Outputs": {
  "ExportsOutputRefMyFirstBucketB888450127863B6E": {
   "Value": {
    "Ref": "MyFirstBucketB8884501"
   },
   "Export": {
    "Name": "StackWithBucketExport:ExportsOutputRefMyFirstBucketB888450127863B6E"
   }
  }
 },
```

Why? Because:
- as soon as it will be imported in other stack it will become a problem
- it introduces the anti pattern of using cross stack dependencies instead of relying on AWS SSM Parameters.


**The question is**: Can we prevent it from happening? If many software developers are contributing to your CDK code, such cross stack reference may slip past code review and become a problem.

In the article below I will find answers to these questions:
- How to enforce that there are no cross stack references in the code?
- What's the CDK tree construct and how it is related to the problem?
- Can we solve the problem with CDK Aspects?
- Can we solve the problem with CDK native validation mechanism?

## CDK Aspects to the rescue - or not?

Our sample CDK app is available [here](https://github.com/BernardOrzechowski/cdk_prevent_cfn_output/blob/develop/src/app.py)

```python
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
```

Its a simple CDK app with 2 stacks, where the 2nd one imports an S3 Bucket created by the first stack. It has the consequence that in cdk.out directory after running `cdk synth` we see that the 1st stack created an Output object and the 2nd stack is importing it (details in this [article](https://medium.com/qoob-dev/cdk-cloud-formation-do-not-follow-blindly-all-best-practices-c529464c8e9d)):



```json
{
 "Resources": {
  "MyFirstBucketB8884501": {
   "Type": "AWS::S3::Bucket",
   "Properties": {
    "BucketName": {
     "Fn::Join": [
      "",
      [
       {
        "Fn::ImportValue": "StackWithBucketExport:ExportsOutputRefMyFirstBucketB888450127863B6E"
       },
       "_2"
    ...
...
```

Currently the command `cdk synth` works. Lets see if we can prevent it.

## CDK Constructs tree

The CDK construct tree is described [here](https://docs.aws.amazon.com/cdk/v2/guide/apps.html#apps-tree)

`cdk synth` produces a.o. the **tree.json** file which is a physical representation of the tree:

![tree.json](images/tree_json.png)



It is a hierarchical structure - a tree with nodes. The stacks are children (nodes) of the App. Stacks have also children. Some of them are regular constructs, but we see also the `CDKMetadata`, `Exports`, `BootstrapVersion` and `CheckBootstrapVersion` nodes. These 4 nodes have predefined names and each has a dedicated role. Within `Exports` the stack exports are stored.

Expanding the `Exports` section we see our `CfnOutput` construct. It was added because the 2nd stack, `StackImportingBucket`, is importing it  in the code (explicit cross stack reference).

```json
          "Exports": {
            "id": "Exports",
            "path": "StackWithBucketExport/Exports",
            "children": {
              "Output{\"Ref\":\"MyFirstBucketB8884501\"}": {
                "id": "Output{\"Ref\":\"MyFirstBucketB8884501\"}",
                "path": "StackWithBucketExport/Exports/Output{\"Ref\":\"MyFirstBucketB8884501\"}",
                "constructInfo": {
                  "fqn": "aws-cdk-lib.CfnOutput",
                  "version": "2.133.0"
                }
              }
            },
            "constructInfo": {
              "fqn": "constructs.Construct",
              "version": "10.4.2"
            }
          }
```


## CDK Native validation mechanism

Now lets try the [CDK Construct IValidation](https://docs.aws.amazon.com/cdk/api/v2/python/constructs/IValidation.html) method. 

We will create a `StackValidator` class that implements the `IValidation` protocol. After the section [CDK Constructs tree](#cdk-constructs-tree) we know that we are looking for the stack node child with ID **"Exports"**.

The code below ([github repo link](https://github.com/BernardOrzechowski/cdk_prevent_cfn_output/blob/develop/src/stacks/cfn_output_validator.py)) checks for the existence of such a child node.

```python

import typing as t

import aws_cdk as cdk
import jsii
from constructs import IConstruct, IValidation

_STACK_CFN_OUTPUT_SECTION: t.Final[str] = "Exports"


@jsii.implements(IValidation)
class StackValidator:
    def __init__(self, stack: cdk.Stack) -> None:
        self.stack = stack

    def validate(self) -> list[str]:
        errors: list[str] = []
        # For each stack child objects (can be e.g.the Exports section from constructs tree (tree.json))
        # run the validation specific for checking if any Output was created
        for child in self.stack.node.children:
            error_messages = self.validate_cfn_output(child)
            if error_messages:
                errors.extend(error_messages)

        return errors

    def validate_cfn_output(self, stack_child_construct: IConstruct) -> list[str]:
        errors: list[str] = []
        print(
            f"Validating construct {stack_child_construct.node.id} in stack {self.stack.node.id}"
        )
        if stack_child_construct.node.id == _STACK_CFN_OUTPUT_SECTION:
            errors.append("CFN Output is not allowed in this stack.")

        return errors

```

When we execute `cdk synth` the error we wanted to see is produced. `cdk synth` failed with the message `CFN Output is not allowed in this stack`:


```python
Validating construct MyFirstBucket in stack StackWithBucketExport
Validating construct CDKMetadata in stack StackWithBucketExport
Validating construct Exports in stack StackWithBucketExport
Validating construct MyFirstBucket in stack StackImportingBucket
Validating construct CDKMetadata in stack StackImportingBucket
jsii.errors.JavaScriptError: 
  @jsii/kernel.RuntimeError: Error: Validation failed with the following errors:
    [StackWithBucketExport] CFN Output is not allowed in this stack.
      at Kernel._Kernel_ensureSync (/tmp/tmpq91vo52y/lib/program.js:927:23)
      at Kernel.invoke (/tmp/tmpq91vo52y/lib/program.js:294:102)
      at KernelHost.processRequest (/tmp/tmpq91vo52y/lib/program.js:15467:36)
      at KernelHost.run (/tmp/tmpq91vo52y/lib/program.js:15427:22)
      at Immediate._onImmediate (/tmp/tmpq91vo52y/lib/program.js:15428:46)
      at process.processImmediate (node:internal/timers:476:21)
```

## Summary





