class Token:
    def __init__(self, type_, value=None, start_position=None, end_position=None):
        self.type = type_
        self.value = value

        if start_position:
            self.start_position = start_position.copy_position()
            self.end_position = start_position.copy_position()
            self.end_position.next_character()

        if end_position:
            self.end_position = end_position.copy_position()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
