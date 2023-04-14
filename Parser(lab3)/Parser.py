from Errors import InvalidSyntaxError
from Lexer import Lexer
# from Nodes import ListNode, ReturnNode, ContinueNode, BreakNode, VarAssignNode, UnaryOperationNode, CallNode, \
#     NumberNode, StringNode, VarAccessNode, IfNode, ForNode, WhileNode, FuncDefinitionNode, BinaryOperationNode
from NodesTree import ListNode, ReturnNode, ContinueNode, BreakNode, VarAssignNode, UnaryOperationNode, CallNode, NumberNode, \
    StringNode, VarAccessNode, IfNode, ForNode, WhileNode, FuncDefinitionNode, BinaryOperationNode
from ParseResult import ParseResult

INT = 'INT'
FLOAT = 'FLOAT'
STRING = 'STRING'
IDENTIFIER = 'IDENTIFIER'
KEYWORD = 'KEYWORD'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
POW = 'POW'
EQ = 'EQ'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LSQUARE = 'LSQUARE'
RSQUARE = 'RSQUARE'
EE = 'EE'
NE = 'NE'
LT = 'LT'
GT = 'GT'
LTE = 'LTE'
GTE = 'GTE'
COMMA = 'COMMA'
ARROW = 'ARROW'
NEWLINE = 'NEWLINE'
EOF = 'EOF'

KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELIF',
    'ELSE',
    'FOR',
    'TO',
    'STEP',
    'WHILE',
    'FUN',
    'THEN',
    'END',
    'RETURN',
    'CONTINUE',
    'BREAK',
]


##################PARSER#####################

class Parser:
    def __init__(self, tokens):
        self.current_token = None
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def advance(self):
        self.token_index += 1
        self.update_current_token()
        return self.current_token

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()
        return self.current_token

    def parse(self):
        result = self.statements()
        if not result.error and self.current_token.type != EOF:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                "token cannot appear after previous tokens"
            ))
        return result

    ###############GRAMMAR####################

    def statements(self):
        result = ParseResult()
        statements = []
        start_position = self.current_token.start_position.copy_position()

        while self.current_token.type == NEWLINE:
            result.register_advancement()
            self.advance()

        statement = result.register(self.statement())
        if result.error:
            return result

        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0

            while self.current_token.type == NEWLINE:
                result.register_advancement()
                self.advance()
                newline_count += 1

            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break

            statement = result.try_to_register(self.statement())

            if not statement:
                self.reverse(result.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return result.success(ListNode(statements, start_position, self.current_token.end_position.copy_position()))

    def statement(self):
        result = ParseResult()
        start_position = self.current_token.start_position.copy_position()

        if self.current_token.matches(KEYWORD, 'RETURN'):
            result.register_advancement()
            self.advance()

            expression = result.try_to_register(self.expression())

            if not expression:
                self.reverse(result.to_reverse_count)

            return result.success(ReturnNode(expression, start_position, self.current_token.start_position.copy_position()))

        if self.current_token.matches(KEYWORD, 'CONTINUE'):
            result.register_advancement()
            self.advance()

            return result.success(ContinueNode(start_position, self.current_token.start_position.copy_position()))

        if self.current_token.matches(KEYWORD, 'BREAK'):
            result.register_advancement()
            self.advance()

            return result.success(BreakNode(start_position, self.current_token.start_position.copy_position()))

        expression = result.register(self.expression())

        if result.error:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                "Expected 'RETURN', 'CONTINUE', 'BREAK', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, "
                "identifier, '+', '-', '(', '[' or 'NOT'"
            ))

        return result.success(expression)

    def expression(self):
        result = ParseResult()

        if self.current_token.matches(KEYWORD, 'VAR'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != IDENTIFIER:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    "Expected identifier"
                ))

            var_name = self.current_token
            result.register_advancement()
            self.advance()

            if self.current_token.type != EQ:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    "Expected '='"
                ))

            result.register_advancement()
            self.advance()
            expression = result.register(self.expression())

            if result.error:
                return result

            return result.success(VarAssignNode(var_name, expression))

        node = result.register(self.binary_operation(self.comp_expression, ((KEYWORD, 'AND'), (KEYWORD, 'OR'))))

        if result.error:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
            ))

        return result.success(node)

    def comp_expression(self):
        result = ParseResult()

        if self.current_token.matches(KEYWORD, 'NOT'):
            op_token = self.current_token
            result.register_advancement()
            self.advance()

            node = result.register(self.comp_expression())

            if result.error:
                return result

            return result.success(UnaryOperationNode(op_token, node))

        node = result.register(self.binary_operation(self.arith_expression, (EE, NE, LT, GT, LTE, GTE)))

        if result.error:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN' or 'NOT'"
            ))

        return result.success(node)

    def arith_expression(self):
        return self.binary_operation(self.term, (PLUS, MINUS))

    def term(self):
        return self.binary_operation(self.factor, (MUL, DIV))

    def factor(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (PLUS, MINUS):
            result.register_advancement()
            self.advance()
            factor = result.register(self.factor())

            if result.error:
                return result

            return result.success(UnaryOperationNode(token, factor))

        return self.power()

    def power(self):
        return self.binary_operation(self.call, (POW,), self.factor)

    def call(self):
        result = ParseResult()
        atom = result.register(self.atom())
        if result.error:
            return result

        if self.current_token.type == LPAREN:
            result.register_advancement()
            self.advance()
            arguments_nodes = []

            if self.current_token.type == RPAREN:
                result.register_advancement()
                self.advance()
            else:
                arguments_nodes.append(result.register(self.expression()))
                if result.error:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.start_position, self.current_token.end_position,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', "
                        "'(', '[' or 'NOT'"
                    ))

                while self.current_token.type == COMMA:
                    result.register_advancement()
                    self.advance()

                    arguments_nodes.append(result.register(self.expression()))

                    if result.error:
                        return result

                if self.current_token.type != RPAREN:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.start_position, self.current_token.end_position,
                        f"Expected ',' or ')'"
                    ))

                result.register_advancement()
                self.advance()

            return result.success(CallNode(atom, arguments_nodes))

        return result.success(atom)

    def atom(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (INT, FLOAT):
            result.register_advancement()
            self.advance()

            return result.success(NumberNode(token))

        elif token.type == STRING:
            result.register_advancement()
            self.advance()

            return result.success(StringNode(token))

        elif token.type == IDENTIFIER:
            result.register_advancement()
            self.advance()

            return result.success(VarAccessNode(token))

        elif token.type == LPAREN:
            result.register_advancement()
            self.advance()
            expression = result.register(self.expression())

            if result.error:
                return result

            if self.current_token.type == RPAREN:
                result.register_advancement()
                self.advance()
                return result.success(expression)
            else:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    "Expected ')'"
                ))

        elif token.type == LSQUARE:
            list_expression = result.register(self.list_expression())

            if result.error:
                return result

            return result.success(list_expression)

        elif token.matches(KEYWORD, 'IF'):
            if_expression = result.register(self.if_expression())

            if result.error:
                return result

            return result.success(if_expression)

        elif token.matches(KEYWORD, 'FOR'):
            for_expression = result.register(self.for_expression())

            if result.error:
                return result

            return result.success(for_expression)

        elif token.matches(KEYWORD, 'WHILE'):
            while_expression = result.register(self.while_expression())

            if result.error:
                return result

            return result.success(while_expression)

        elif token.matches(KEYWORD, 'FUN'):
            func_definition = result.register(self.func_definition())

            if result.error:
                return result

            return result.success(func_definition)

        return result.failure(InvalidSyntaxError(
            token.start_position, token.end_position,
            "Expected int, float, identifier, '+', '-', '(', '[', IF', 'FOR', 'WHILE', 'FUN'"
        ))

    def list_expression(self):
        result = ParseResult()
        element_nodes = []
        start_position = self.current_token.start_position.copy_position()

        if self.current_token.type != LSQUARE:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected '['"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == RSQUARE:
            result.register_advancement()
            self.advance()
        else:
            element_nodes.append(result.register(self.expression()))
            if result.error:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    "Expected ']', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', "
                    "'(', '[' or 'NOT'"
                ))

            while self.current_token.type == COMMA:
                result.register_advancement()
                self.advance()

                element_nodes.append(result.register(self.expression()))

                if result.error:
                    return result

            if self.current_token.type != RSQUARE:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected ',' or ']'"
                ))

            result.register_advancement()
            self.advance()

        return result.success(ListNode(
            element_nodes,
            start_position,
            self.current_token.end_position.copy_position()
        ))

    def if_expression(self):
        result = ParseResult()
        all_cases = result.register(self.if_expression_cases('IF'))

        if result.error:
            return result

        cases, else_case = all_cases

        return result.success(IfNode(cases, else_case))

    def if_expression_b(self):
        return self.if_expression_cases('ELIF')

    def if_expression_c(self):
        result = ParseResult()
        else_case = None

        if self.current_token.matches(KEYWORD, 'ELSE'):
            result.register_advancement()
            self.advance()

            if self.current_token.type == NEWLINE:
                result.register_advancement()
                self.advance()

                statements = result.register(self.statements())

                if result.error:
                    return result

                else_case = (statements, True)

                if self.current_token.matches(KEYWORD, 'END'):
                    result.register_advancement()
                    self.advance()
                else:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.start_position, self.current_token.end_position,
                        "Expected 'END'"
                    ))
            else:
                expression = result.register(self.statement())

                if result.error:
                    return result

                else_case = (expression, False)

        return result.success(else_case)

    def if_expression_b_or_c(self):
        result = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(KEYWORD, 'ELIF'):
            all_cases = result.register(self.if_expression_b())
            if result.error:
                return result
            cases, else_case = all_cases
        else:
            else_case = result.register(self.if_expression_c())

            if result.error:
                return result

        return result.success((cases, else_case))

    def if_expression_cases(self, case_keyword):
        result = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(KEYWORD, case_keyword):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected '{case_keyword}'"
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expression())

        if result.error:
            return result

        if not self.current_token.matches(KEYWORD, 'THEN'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'THEN'"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == NEWLINE:
            result.register_advancement()
            self.advance()

            statements = result.register(self.statements())

            if result.error:
                return result

            cases.append((condition, statements, True))

            if self.current_token.matches(KEYWORD, 'END'):
                result.register_advancement()
                self.advance()
            else:
                all_cases = result.register(self.if_expression_b_or_c())

                if result.error:
                    return result

                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expression = result.register(self.statement())

            if result.error:
                return result

            cases.append((condition, expression, False))

            all_cases = result.register(self.if_expression_b_or_c())

            if result.error:
                return result

            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return result.success((cases, else_case))

    def for_expression(self):
        result = ParseResult()

        if not self.current_token.matches(KEYWORD, 'FOR'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'FOR'"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type != IDENTIFIER:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected identifier"
            ))

        var_name = self.current_token
        result.register_advancement()
        self.advance()

        if self.current_token.type != EQ:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected '='"
            ))

        result.register_advancement()
        self.advance()

        start_value = result.register(self.expression())

        if result.error:
            return result

        if not self.current_token.matches(KEYWORD, 'TO'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'TO'"
            ))

        result.register_advancement()
        self.advance()

        end_value = result.register(self.expression())

        if result.error:
            return result

        if self.current_token.matches(KEYWORD, 'STEP'):
            result.register_advancement()
            self.advance()

            step_value = result.register(self.expression())

            if result.error:
                return result
        else:
            step_value = None

        if not self.current_token.matches(KEYWORD, 'THEN'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'THEN'"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == NEWLINE:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements())

            if result.error:
                return result

            if not self.current_token.matches(KEYWORD, 'END'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected 'END'"
                ))

            result.register_advancement()
            self.advance()

            return result.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = result.register(self.statement())

        if result.error:
            return result

        return result.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expression(self):
        result = ParseResult()

        if not self.current_token.matches(KEYWORD, 'WHILE'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'WHILE'"
            ))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expression())

        if result.error:
            return result

        if not self.current_token.matches(KEYWORD, 'THEN'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'THEN'"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == NEWLINE:
            result.register_advancement()
            self.advance()

            body = result.register(self.statements())

            if result.error:
                return result

            if not self.current_token.matches(KEYWORD, 'END'):
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected 'END'"
                ))

            result.register_advancement()
            self.advance()

            return result.success(WhileNode(condition, body, True))

        body = result.register(self.statement())

        if result.error:
            return result

        return result.success(WhileNode(condition, body, False))

    def func_definition(self):
        result = ParseResult()

        if not self.current_token.matches(KEYWORD, 'FUN'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'FUN'"
            ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == IDENTIFIER:
            var_name_token = self.current_token
            result.register_advancement()
            self.advance()

            if self.current_token.type != LPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected '('"
                ))
        else:
            var_name_token = None

            if self.current_token.type != LPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected identifier or '('"
                ))

        result.register_advancement()
        self.advance()
        arguments_name_tokens = []

        if self.current_token.type == IDENTIFIER:
            arguments_name_tokens.append(self.current_token)
            result.register_advancement()
            self.advance()

            while self.current_token.type == COMMA:
                result.register_advancement()
                self.advance()

                if self.current_token.type != IDENTIFIER:
                    return result.failure(InvalidSyntaxError(
                        self.current_token.start_position, self.current_token.end_position,
                        f"Expected identifier"
                    ))

                arguments_name_tokens.append(self.current_token)
                result.register_advancement()
                self.advance()

            if self.current_token.type != RPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != RPAREN:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_position, self.current_token.end_position,
                    f"Expected identifier or ')'"
                ))

        result.register_advancement()
        self.advance()

        if self.current_token.type == ARROW:
            result.register_advancement()
            self.advance()

            body = result.register(self.expression())

            if result.error:
                return result

            return result.success(FuncDefinitionNode(
                var_name_token,
                arguments_name_tokens,
                body,
                True
            ))

        if self.current_token.type != NEWLINE:
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected '->' or NEWLINE"
            ))

        result.register_advancement()
        self.advance()

        body = result.register(self.statements())

        if result.error:
            return result

        if not self.current_token.matches(KEYWORD, 'END'):
            return result.failure(InvalidSyntaxError(
                self.current_token.start_position, self.current_token.end_position,
                f"Expected 'END'"
            ))

        result.register_advancement()
        self.advance()

        return result.success(FuncDefinitionNode(
            var_name_token,
            arguments_name_tokens,
            body,
            False
        ))

    ###################################

    def binary_operation(self, func_a, ops, func_b=None):

        if func_b is None:
            func_b = func_a

        result = ParseResult()
        left = result.register(func_a())

        if result.error:
            return result

        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_token = self.current_token
            result.register_advancement()
            self.advance()
            right = result.register(func_b())

            if result.error:
                return result

            left = BinaryOperationNode(left, op_token, right)

        return result.success(left)


text = '''
FUN fact(n)
	VAR result = 1
	IF n < 0 THEN
	    PRINT("Error! Factorial of a negative number doesn't exist.")
	ELSE
	    FOR i = l TO n+1 THEN
		    VAR result = result * i
	    END
    END
	RETURN result
END

VAR a = fact(5)
PRINT(a)
'''

test = '''
	 WHILE next <= n THEN
	    PRINT(next)
        VAR el1 = el2
        VAR el2 = next
        VAR next = el1 + el2
        ELSE THEN
    END
'''

lexer = Lexer('<stdin>', test)
tokens, error = lexer.make_tokens()

parser = Parser(tokens)
ast = parser.parse()
if ast.error:
    print(ast.error.string_representation())
else:
    symbol = "--"
    result = ""
    count_bracket = 0
    ast_tree = str(ast.node)
    for i in range(len(ast_tree)):
        if ast_tree[i] == "(":
            count_bracket += 1
            pattern = "\n" + count_bracket * symbol
            result = result + pattern
        elif ast_tree[i] == ")":
            count_bracket -= 1
        else:
            result = result + ast_tree[i]

    print(result)
    # print(ast.node)

# def run(fn, text):
#     # Generate tokens
#     lexer = Lexer(fn, text)
#     tokens, error = lexer.make_tokens()
#     if error: return None, error
#
#     # Generate AST
#     parser = Parser(tokens)
#     ast = parser.parse()
#     if ast.error: return None, ast.error
#
#     # Run program
#     interpreter = Interpreter()
#     context = Context('<program>')
#     context.symbol_table = global_symbol_table
#     result = interpreter.visit(ast.node, context)
#
#     return result.value, result.error
