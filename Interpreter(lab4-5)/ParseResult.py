class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_count_advance = 0
        self.count_advance = 0
        self.to_reverse_count = 0

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_count_advance == 0:
            self.error = error
        return self

    def register(self, result):
        self.last_registered_count_advance = result.count_advance
        self.count_advance += result.count_advance
        if result.error: self.error = result.error
        return result.node

    def try_to_register(self, result):
        if result.error:
            self.to_reverse_count = result.count_advance
            return None
        return self.register(result)

    def register_advancement(self):
        self.last_registered_count_advance = 1
        self.count_advance += 1
