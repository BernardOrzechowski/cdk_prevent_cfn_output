
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

## CDK Constructs tree

## CDK Native validation mechanism

## Summary





