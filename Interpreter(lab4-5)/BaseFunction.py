from Context import Context
from Errors import RTError
from RTResult import RTResult
from SymbolTable import SymbolTable
from Value import Value


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.start_position)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_arguments(self, arguments_names, arguments):
        res = RTResult()

        if len(arguments) > len(arguments_names):
            return res.failure(RTError(
                self.start_position, self.end_position,
                f"{len(arguments) - len(arguments_names)} too many arguments passed into {self}",
                self.context
            ))

        if len(arguments) < len(arguments_names):
            return res.failure(RTError(
                self.start_position, self.end_position,
                f"{len(arguments_names) - len(arguments)} too few arguments passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_arguments(self, arguments_names, arguments, exec_ctx):
        for i in range(len(arguments)):
            arguments_name = arguments_names[i]
            arguments_value = arguments[i]
            arguments_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arguments_name, arguments_value)

    def check_and_populate_arguments(self, arguments_names, arguments, exec_ctx):
        res = RTResult()
        res.register(self.check_arguments(arguments_names, arguments))
        if res.should_return(): return res
        self.populate_arguments(arguments_names, arguments, exec_ctx)
        return res.success(None)
