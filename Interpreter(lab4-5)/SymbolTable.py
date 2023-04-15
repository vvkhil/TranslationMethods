class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def remove(self, name):
        del self.symbols[name]

    def set(self, name, value):
        self.symbols[name] = value

    def get(self, name):
        value = self.symbols.get(name, None)

        if value is None and self.parent:
            return self.parent.get(name)

        return value