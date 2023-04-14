class Position:
    def __init__(self, index, line, colon, function, function_text):
        self.index = index
        self.line = line
        self.colon = colon
        self.function = function
        self.function_text = function_text

    def next_character(self, current_character=None):
        self.index += 1
        self.colon += 1

        if current_character == '\n':
            self.line += 1
            self.colon = 0

        return self

    def copy_position(self):
        return Position(self.index, self.line, self.colon, self.function, self.function_text)