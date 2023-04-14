class ListNode:
    def __init__(self, nodes, start_position, end_position):
        self.nodes = nodes

        self.start_position = start_position
        self.end_position = end_position

    def __repr__(self):
        return f'\033[91m\nListNodes:\n{self.nodes}\033[91m]'


class NumberNode:
    def __init__(self, token):
        self.token = token

        self.start_position = self.token.start_position
        self.end_position = self.token.end_position

    def __repr__(self):
        return f'\033[31m[Type:{self.token.type}, Value:{self.token.value}\033[31m]'


class StringNode:
    def __init__(self, token):
        self.token = token

        self.start_position = self.token.start_position
        self.end_position = self.token.end_position

    def __repr__(self):
        return f'\033[31m[Type:{self.token.type}, Value:{self.token.value}\033[31m]'


class BinaryOperationNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

        self.start_position = self.left_node.start_position
        self.end_position = self.right_node.end_position

    def __repr__(self):
        return f'\033[35mBinOpNode:\n\033[35m[LeftNode:{self.left_node}, \033[35mOperation:{self.op_token},' \
               f' \033[35mRightNode:{self.right_node}\033[35m]'


class UnaryOperationNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

        self.start_position = self.op_token.start_position
        self.end_position = node.end_position

    def __repr__(self):
        return f'\033[35mUnaryOpNode:[Operation:{self.op_token}, \033[35mNodeUnary:{self.node}\033[35m]'


class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.start_position = self.var_name_token.start_position
        self.end_position = self.value_node.end_position

    def __repr__(self):
        return f'\033[34m\nVarAssignNode:[TypeVar:{self.var_name_token}, \033[34mValue:{self.value_node}\033[34m]'


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.start_position = self.var_name_token.start_position
        self.end_position = self.var_name_token.end_position

    def __repr__(self):
        return f'\033[33mVarAccessNode:[{self.var_name_token}]\033[33m'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.start_position = self.cases[0][0].start_position
        self.end_position = (self.else_case or self.cases[len(self.cases) - 1])[0].end_position

    def __repr__(self):
        return f'\033[36m\nIfNode:\n[Cases:\n{self.cases},\n\033[36mElse:\n{self.else_case}\033[36m]'


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.start_position = self.var_name_token.start_position
        self.end_position = self.body_node.end_position

    def __repr__(self):
        return f'\033[37m\nForNode:\n[VarName:{self.var_name_token}, \n\033[37mStartValue:{self.start_value_node}, ' \
               f'\n\033[37mEndValue:{self.end_value_node}, ' \
               f'\n\033[37mStep:{self.step_value_node}, \n\033[37mBodyFor:{self.body_node}\033[37m]'


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.start_position = self.condition_node.start_position
        self.end_position = self.body_node.end_position

    def __repr__(self):
        return f'\033[37m\nWhileNode:\n[ConditionWhile:\n{self.condition_node}, ' \
               f'\n\033[37mBodyWhile:\n{self.body_node}\033[37m]'


class BreakNode:
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position


class ContinueNode:
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position


class FuncDefinitionNode:
    def __init__(self, var_name_token, arguments_name_tokens, body_node, should_auto_return):
        self.var_name_token = var_name_token
        self.arguments_name_tokens = arguments_name_tokens
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_token:
            self.start_position = self.var_name_token.start_position

        elif len(self.arguments_name_tokens) > 0:
            self.start_position = self.arguments_name_tokens[0].start_position

        else:
            self.start_position = self.body_node.start_position

        self.end_position = self.body_node.end_position

    def __repr__(self):
        return f'\033[0m\nFuncDefNode:\n[VarName:{self.var_name_token}, ' \
               f'\n\033[0mArgNameFunc:{self.arguments_name_tokens}, ' \
               f'\n\033[0mBody:\n{self.body_node}\033[0m]'


class CallNode:
    def __init__(self, node_to_call, arguments_nodes):
        self.node_to_call = node_to_call
        self.arguments_nodes = arguments_nodes

        self.start_position = self.node_to_call.start_position

        if len(self.arguments_nodes) > 0:
            self.end_position = self.arguments_nodes[len(self.arguments_nodes) - 1].end_position
        else:
            self.end_position = self.node_to_call.end_position

    def __repr__(self):
        return f'\033[32m\nCallNode:\n[NodeToCall:\n{self.node_to_call}, ' \
               f'\n\033[32mArgNodeToCall:{self.arguments_nodes}\033[32m]'


class ReturnNode:
    def __init__(self, node_to_return, start_position, end_position):
        self.node_to_return = node_to_return

        self.start_position = start_position
        self.end_position = end_position

    def __repr__(self):
        return f'\033[32m\nReturnNode:[Return:{self.node_to_return}\033[32m]'