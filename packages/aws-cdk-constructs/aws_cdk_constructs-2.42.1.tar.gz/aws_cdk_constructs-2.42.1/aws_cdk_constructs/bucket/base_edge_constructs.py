import builtins
import aws_cdk
import constructs


class BaseEdgeConstruct(constructs.Construct):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        """
        :param scope: -
        :param id: -
        """

        super().__init__(scope, id)

        self._stack = aws_cdk.Stack.of(self)

        self._edge_stack = (
            self.get_or_create_cross_region_support_stack()
            if self.stack.region != 'us-east-1'
            else self.stack
        )

    @property
    def stack(self):
        return self._stack

    @property
    def edge_stack(self):
        return self._edge_stack

    def get_or_create_cross_region_support_stack(self) -> aws_cdk.Stack:

        stack = self.stack.nested_stack_parent or self.stack
        account = stack.account
        stack_name = stack.stack_name
        stack_id = 'lambda-cloudfront-support-stack'
        app = self.require_app()

        support_stack: aws_cdk.Stack = app.node.try_find_child(stack_id)

        if support_stack is None:
            support_stack = aws_cdk.Stack(
                app,
                stack_id,
                stack_name=f'{stack_name}-support-lambda-cloudfront',
                env={'account': account, 'region': 'us-east-1'},
            )

        # the stack containing the edge lambdas must be deployed before
        self.stack.add_dependency(support_stack)

        return support_stack

    def require_app(self) -> aws_cdk.App:

        app = self.node.root

        if app is None or aws_cdk.App.is_app(app) is False:
            raise Exception(
                'Stacks which uses edge constructs must be part of a CDK app'
            )

        return app
