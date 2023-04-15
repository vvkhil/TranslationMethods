import os

from BaseFunction import BaseFunction
from Context import Context
from Errors import RTError
from Lexer import Lexer
from List import List
from Number import Number
from Parser import Parser
from RTResult import RTResult
from String import String
from SymbolTable import SymbolTable

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


class Function(BaseFunction):
    def __init__(self, name, body_node, arguments_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arguments_names = arguments_names
        self.should_auto_return = should_auto_return

    def execute(self, arguments):
        res = RTResult()
        interpreter = Interpreter()
        execute_context = self.generate_new_context()

        res.register(self.check_and_populate_arguments(self.arguments_names, arguments, execute_context))
        if res.should_return():
            return res

        value = res.register(interpreter.visit_method(self.body_node, execute_context))
        if res.should_return() and res.func_return_value is None:
            return res

        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null

        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arguments_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_position(self.start_position, self.end_position)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, arguments):
        res = RTResult()
        execute_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_arguments(method.arguments_names, arguments, execute_context))

        if res.should_return():
            return res

        return_value = res.register(method(execute_context))

        if res.should_return():
            return res

        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_position(self.start_position, self.end_position)

        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    #####################################

    def execute_input(self, execute_context):
        text = input()

        return RTResult().success(String(text))

    def execute_input_int(self, execute_context):
        while True:

            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")

        return RTResult().success(Number(number))

    def execute_print(self, execute_context):
        print(str(execute_context.symbol_table.get('value')))

        return RTResult().success(Number.null)

    def execute_print_ret(self, execute_context):
        return RTResult().success(String(str(execute_context.symbol_table.get('value'))))

    def execute_clear(self, execute_context):
        os.system('cls' if os.name == 'nt' else 'cls')

        return RTResult().success(Number.null)

    def execute_is_string(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get("value"), String)

        return RTResult().success(Number.true if is_number else Number.false)

    def execute_is_number(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get("value"), Number)

        return RTResult().success(Number.true if is_number else Number.false)

    def execute_is_function(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get("value"), BaseFunction)

        return RTResult().success(Number.true if is_number else Number.false)

    def execute_is_list(self, execute_context):
        is_number = isinstance(execute_context.symbol_table.get("value"), List)

        return RTResult().success(Number.true if is_number else Number.false)

    def execute_len(self, execute_context):
        list_ = execute_context.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "argument must be list",
                execute_context
            ))

        return RTResult().success(Number(len(list_.elements)))

    def execute_append(self, execute_context):
        list_ = execute_context.symbol_table.get("list")
        value = execute_context.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "First argument must be list",
                execute_context
            ))

        list_.elements.append(value)

        return RTResult().success(Number.null)

    def execute_extend(self, execute_context):
        first_list = execute_context.symbol_table.get("first_list")
        second_list = execute_context.symbol_table.get("second_list")

        if not isinstance(first_list, List):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "First argument must be list",
                execute_context
            ))

        if not isinstance(second_list, List):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "Second argument must be list",
                execute_context
            ))

        first_list.elements.extend(second_list.elements)

        return RTResult().success(Number.null)

    def execute_pop(self, execute_context):
        list_ = execute_context.symbol_table.get("list")
        index = execute_context.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "First argument must be list",
                execute_context
            ))

        if not isinstance(index, Number):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "Second argument must be number",
                execute_context
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                'Element at this index could not be removed from list because index is out of bounds',
                execute_context
            ))

        return RTResult().success(element)

    def execute_run(self, execute_context):
        fn = execute_context.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                "Second argument must be string",
                execute_context
            ))

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                f"Failed to load script \"{fn}\"\n" + str(e),
                execute_context
            ))

        _, error = run(fn, script)

        if error:
            return RTResult().failure(RTError(
                self.start_position, self.end_position,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.string_representation(),
                execute_context
            ))

        return RTResult().success(Number.null)

    execute_input.arguments_names = []
    execute_input_int.arguments_names = []
    execute_print.arguments_names = ['value']
    execute_print_ret.arguments_names = ['value']
    execute_clear.arguments_names = []
    execute_is_string.arguments_names = ["value"]
    execute_is_number.arguments_names = ["value"]
    execute_is_function.arguments_names = ["value"]
    execute_is_list.arguments_names = ["value"]
    execute_len.arguments_names = ["list"]
    execute_append.arguments_names = ["list", "value"]
    execute_extend.arguments_names = ["first_list", "second_list"]
    execute_extend.arguments_names = ["first_list", "second_list"]
    execute_run.arguments_names = ["fn"]


BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.run = BuiltInFunction("run")

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null)
global_symbol_table.set("FALSE", Number.false)
global_symbol_table.set("TRUE", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("PRINT", BuiltInFunction.print)
global_symbol_table.set("PRINT_RET", BuiltInFunction.print_ret)
global_symbol_table.set("INPUT", BuiltInFunction.input)
global_symbol_table.set("INPUT_INT", BuiltInFunction.input_int)
global_symbol_table.set("CLEAR", BuiltInFunction.clear)
global_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("IS_NUM", BuiltInFunction.is_number)
global_symbol_table.set("IS_STR", BuiltInFunction.is_string)
global_symbol_table.set("IS_LIST", BuiltInFunction.is_list)
global_symbol_table.set("IS_FUN", BuiltInFunction.is_function)
global_symbol_table.set("APPEND", BuiltInFunction.append)
global_symbol_table.set("POP", BuiltInFunction.pop)
global_symbol_table.set("EXTEND", BuiltInFunction.extend)
global_symbol_table.set("LEN", BuiltInFunction.len)
global_symbol_table.set("RUN", BuiltInFunction.run)


class Interpreter:
    def visit_method(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    ###################################

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.nodes:
            elements.append(res.register(self.visit_method(element_node, context)))

            if res.should_return():
                return res

        return res.success(
            List(elements).set_context(context).set_position(node.start_position, node.end_position)
        )

    def visit_BinaryOperationNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit_method(node.left_node, context))

        if res.should_return():
            return res

        right = res.register(self.visit_method(node.right_node, context))

        if res.should_return():
            return res

        elif node.op_token.type == MUL:
            result, error = left.multed_by(right)

        elif node.op_token.type == DIV:
            result, error = left.dived_by(right)

        if node.op_token.type == PLUS:
            result, error = left.added_to(right)

        elif node.op_token.type == MINUS:
            result, error = left.subbed_by(right)

        elif node.op_token.type == POW:
            result, error = left.powed_by(right)

        elif node.op_token.type == EE:
            result, error = left.get_comparison_eq(right)

        elif node.op_token.type == NE:
            result, error = left.get_comparison_ne(right)

        elif node.op_token.type == GT:
            result, error = left.get_comparison_gt(right)

        elif node.op_token.type == GTE:
            result, error = left.get_comparison_gte(right)

        elif node.op_token.type == LT:
            result, error = left.get_comparison_lt(right)

        elif node.op_token.type == LTE:
            result, error = left.get_comparison_lte(right)

        elif node.op_token.matches(KEYWORD, 'AND'):
            result, error = left.anded_by(right)

        elif node.op_token.matches(KEYWORD, 'OR'):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_position(node.start_position, node.end_position))

    def visit_UnaryOperationNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit_method(node.node, context))

        if res.should_return():
            return res

        error = None

        if node.op_token.type == MINUS:
            number, error = number.multed_by(Number(-1))

        elif node.op_token.matches(KEYWORD, 'NOT'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_position(node.start_position, node.end_position))

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.token.value).set_context(context).set_position(node.start_position, node.end_position)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.token.value).set_context(context).set_position(node.start_position, node.end_position)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.start_position, node.end_position,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_position(node.start_position, node.end_position).set_context(context)

        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_token.value
        value = res.register(self.visit_method(node.value_node, context))

        if res.should_return():
            return res

        context.symbol_table.set(var_name, value)

        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit_method(condition, context))

            if res.should_return():
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit_method(expr, context))

                if res.should_return():
                    return res

                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit_method(expr, context))

            if res.should_return():
                return res

            return res.success(Number.null if should_return_null else expr_value)

        return res.success(Number.null)

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit_method(node.condition_node, context))

            if res.should_return():
                return res

            if not condition.is_true():
                break

            value = res.register(self.visit_method(node.body_node, context))

            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_position(node.start_position, node.end_position)
        )

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit_method(node.start_value_node, context))

        if res.should_return():
            return res

        end_value = res.register(self.visit_method(node.end_value_node, context))

        if res.should_return():
            return res

        if node.step_value_node:
            step_value = res.register(self.visit_method(node.step_value_node, context))

            if res.should_return():
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_token.value, Number(i))
            i += step_value.value

            value = res.register(self.visit_method(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_position(node.start_position, node.end_position)
        )

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()

    def visit_FuncDefinitionNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_token.value if node.var_name_token else None
        body_node = node.body_node
        arguments_names = [arguments_name.value for arguments_name in node.arguments_name_tokens]
        func_value = Function(func_name, body_node, arguments_names, node.should_auto_return).set_context(
            context).set_position(
            node.start_position, node.end_position)

        if node.var_name_token:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        arguments = []

        value_to_call = res.register(self.visit_method(node.node_to_call, context))

        if res.should_return():
            return res

        value_to_call = value_to_call.copy().set_position(node.start_position, node.end_position)

        for arguments_node in node.arguments_nodes:
            arguments.append(res.register(self.visit_method(arguments_node, context)))

            if res.should_return():
                return res

        return_value = res.register(value_to_call.execute(arguments))

        if res.should_return():
            return res

        return_value = return_value.copy().set_position(node.start_position, node.end_position).set_context(context)

        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit_method(node.node_to_return, context))

            if res.should_return():
                return res

        else:
            value = Number.null

        return res.success_return(value)

###############RUN########################

def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

text = '''
VAR el = [1, 2, 3, 4]
FUN min(elements)
    VAR new_elements = []
    
    VAR check = 99999999
    FOR i = 0 TO LEN(elements) THEN
        IF elements/i < check THEN
            VAR check = elements/i
        END
    END
    RETURN check
END    
    
PRINT(min(el))
'''

test = '''
VAR a = [777, 4, 2]
VAR b = [9, 8, -1.56]

VAR c = a * b

FUN min(elements)
    VAR new_elements = []

    VAR check = 99999999
    FOR i = 0 TO LEN(elements) THEN
        IF elements/i < check THEN
            VAR check = elements/i
        END
    END
    RETURN check
END

FUN max(elements)
    VAR new_elements = []

    VAR check = -99999999
    FOR i = 0 TO LEN(elements) THEN
        IF elements/i > check THEN
            VAR check = elements/i
        END
    END
    RETURN check
END

PRINT(c)
PRINT(min(c))
PRINT(max(c))
'''

# Generate tokens
lexer = Lexer('<stdin>', test)
tokens, error = lexer.make_tokens()
if error:
    print(error.string_representation())

# Generate AST
parser = Parser(tokens)
ast = parser.parse()
if ast.error:
    print(ast.error.string_representation())

# Run program
interpreter = Interpreter()
context = Context('<program>')
context.symbol_table = global_symbol_table
result = interpreter.visit_method(ast.node, context)

if result.error:
    print(result.error.string_representation())
else:
    result.value
