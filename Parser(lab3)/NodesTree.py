class ListNode:
    def __init__(self, element_nodes, start_position, end_position):
        self.element_nodes = element_nodes

        self.start_position = start_position
        self.end_position = end_position

    def __repr__(self):
        return f'\n\033[91mListNodes:{self.element_nodes}\033[91m'


class NumberNode:
    def __init__(self, token):
        self.token = token

        self.start_position = self.token.start_position
        self.end_position = self.token.end_position

    def __repr__(self):
        return f'(\033[31mType:{self.token.type}, (\033[31mValue:{self.token.value}\033[31m)\033[31m)'


class StringNode:
    def __init__(self, token):
        self.token = token

        self.start_position = self.token.start_position
        self.end_position = self.token.end_position

    def __repr__(self):
        return f'(\033[31mType:{self.token.type}, (\033[31mValue:{self.token.value}\033[31m)\033[31m)'


class BinaryOperationNode:
    def __init__(self, left_node, operation_token, right_node):
        self.left_node = left_node
        self.operation_token = operation_token
        self.right_node = right_node

        self.start_position = self.left_node.start_position
        self.end_position = self.right_node.end_position

    def __repr__(self):
        return f'(\033[35mBinOpNode:(\033[35mLeftNode:{self.left_node}, (\033[35mOperation:{self.operation_token},' \
               f'(\033[35mRightNode:{self.right_node}\033[35m)\033[35m)\033[35m)\033[35m)'


class UnaryOperationNode:
    def __init__(self, operation_token, node):
        self.operation_token = operation_token
        self.node = node

        self.start_position = self.operation_token.start_position
        self.end_position = node.end_position

    def __repr__(self):
        return f'(\033[35mUnaryOpNode:(\033[35mOperation:{self.operation_token}, (\033[35mNodeUnary:{self.node}' \
               f'\033[35m)\033[35m)\033[35m)'


class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.start_position = self.var_name_token.start_position
        self.end_position = self.var_name_token.end_position

    def __repr__(self):
        return f'(\033[33mVarAccessNode:(\033[33m{self.var_name_token}\033[33m)\033[33m)'


class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

        self.start_position = self.var_name_token.start_position
        self.end_position = self.value_node.end_position

    def __repr__(self):
        return f'(\033[34mVarAssignNode:(\033[34mTypeVar:{self.var_name_token}, (\033[34mValue:{self.value_node}' \
               f'\033[34m)\033[34m)\033[34m)'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.start_position = self.cases[0][0].start_position
        self.end_position = (self.else_case or self.cases[len(self.cases) - 1])[0].end_position

    def __repr__(self):
        return f'(\033[36mIfNode:(\033[36mCases:{self.cases}, (\033[36mElse:{self.else_case}\033[36m)\033[36m)\033[36m)'


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
        return f'(\033[37mForNode:(\033[37mVarName:{self.var_name_token}, ' \
               f'(\033[37mStartValue:{self.start_value_node}, ' \
               f'(\033[37mEndValue:{self.end_value_node}, ' \
               f'(\033[37mStep:{self.step_value_node}, (\033[37mBodyFor:{self.body_node}\033[37m)\033[37m)\033[37m)' \
               f'\033[37m)\033[37m)\033[37m)'


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.start_position = self.condition_node.start_position
        self.end_position = self.body_node.end_position

    def __repr__(self):
        return f'(\033[37mWhileNode:(\033[37mConditionWhile:{self.condition_node}, ' \
               f'(\033[37mBodyWhile:{self.body_node}\033[37m)\033[37m)\033[37m)'


class ContinueNode:
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position


class BreakNode:
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
        return f'(\033[0mFuncDefNode:(\033[0mVarName:{self.var_name_token}, ' \
               f'(\033[0mArgNameFunc:{self.arguments_name_tokens}, ' \
               f'(\033[0mBody:{self.body_node}\033[0m)\033[0m)\033[0m)\033[0m)'


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
        return f'(\033[32mCallNode:(\033[32mNodeToCall:{self.node_to_call}, ' \
               f'(\033[32mArgNodeToCall:{self.arguments_nodes}\033[32m)\033[32m)\033[32m)'


class ReturnNode:
    def __init__(self, node_to_return, start_position, end_position):
        self.node_to_return = node_to_return

        self.start_position = start_position
        self.end_position = end_position

    def __repr__(self):
        return f'(\033[32mReturnNode:(\033[32mReturn:{self.node_to_return}\033[32m)\033[32m)'
