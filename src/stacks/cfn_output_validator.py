import typing as t

import aws_cdk as cdk
import jsii
from constructs import IConstruct, IValidation
from loguru import logger

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
        logger.info(
            f"Validating construct {stack_child_construct.node.id} in stack {self.stack.node.id}"
        )
        if stack_child_construct.node.id == _STACK_CFN_OUTPUT_SECTION:
            errors.append("CFN Output is not allowed in this stack.")

        return errors
