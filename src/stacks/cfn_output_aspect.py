import aws_cdk as cdk
import jsii
from constructs import IConstruct
from loguru import logger


@jsii.implements(cdk.IAspect)
class CfnOutputAspect:
    """Aspect to validate that no CFN Outputs are created in the stack."""

    def visit(self, node: IConstruct):
        logger.info(f"Visiting node {node.node.id}")
        if isinstance(node, cdk.CfnOutput):
            cdk.Annotations.of(node).add_error(
                '"CFN Output is not allowed in this stack."'
            )
