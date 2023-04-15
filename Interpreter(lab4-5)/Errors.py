from strings_with_error import arrow_string


class Error:
    def __init__(self, start_position, end_position, error_name, details):
        self.start_position = start_position
        self.end_position = end_position
        self.error_name = error_name
        self.details = details

    def string_representation(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.start_position.function}, line {self.start_position.line + 1}'
        result += '\n\n' + arrow_string(self.start_position.function_text, self.start_position, self.end_position)
        return result


class IllegalCharError(Error):
    def __init__(self, start_position, end_position, details):
        super().__init__(start_position, end_position, 'Illegal Character', details)


class ExpectedCharError(Error):
    def __init__(self, start_position, end_position, details):
        super().__init__(start_position, end_position, 'Expected Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, start_position, end_position, details=''):
        super().__init__(start_position, end_position, 'Invalid Syntax', details)


class RTError(Error):
    def __init__(self, start_position, end_position, details, context):
        super().__init__(start_position, end_position, 'Runtime Error', details)
        self.context = context

    def string_repr(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + arrow_string(self.start_position.function_text, self.start_position, self.end_position)
        return result

    def generate_traceback(self):
        result = ''
        position = self.start_position
        ctx = self.context

        while ctx:
            result = f'\tFile {position.function}, line {str(position.line + 1)}, in {ctx.display_name}\n' + result
            position = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result
