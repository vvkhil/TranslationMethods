import string

from Errors import IllegalCharError, ExpectedCharError
from Position import Position
from Token import Token

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
# TOKENS
#######################################

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
INT = 'INT'
FLOAT = 'FLOAT'
STRING = 'STRING'
IDENTIFIER = 'IDENTIFIER'
KEYWORD = 'KEYWORD'
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
    'VAR',
    'AND',
    'OR',
    'NOT',
    'IF',
    'ELIF',
    'ELSE'
]

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, function, text):
        self.function = function
        self.text = text
        self.position = Position(-1, 0, -1, function, text)
        self.current_character = None
        self.next_character()

    def next_character(self):
        self.position.next_character(self.current_character)
        if self.position.index < len(self.text):
            self.current_character = self.text[self.position.index]
        else:
            self.current_character = None

    def make_tokens(self):
        tokens = []

        while self.current_character != None:
            if self.current_character in ' \t':
                self.next_character()
            elif self.current_character == '(':
                tokens.append(Token(LPAREN, start_position=self.position))
                self.next_character()
            elif self.current_character == ')':
                tokens.append(Token(RPAREN, start_position=self.position))
                self.next_character()
            elif self.current_character == '[':
                tokens.append(Token(LSQUARE, start_position=self.position))
                self.next_character()
            elif self.current_character == ']':
                tokens.append(Token(RSQUARE, start_position=self.position))
                self.next_character()
            elif self.current_character == '!':
                token, error = self.make_token_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_character == '#':
                self.skip_comment()
            elif self.current_character in ';\n':
                tokens.append(Token(NEWLINE, start_position=self.position))
                self.next_character()
            elif self.current_character == '^':
                tokens.append(Token(POW, start_position=self.position))
                self.next_character()
            elif self.current_character == '=':
                tokens.append(self.make_token_equals())
            elif self.current_character == '<':
                tokens.append(self.make_token_less_than())
            elif self.current_character == '>':
                tokens.append(self.make_token_greater_than())
            elif self.current_character == ',':
                tokens.append(Token(COMMA, start_position=self.position))
                self.next_character()
            elif self.current_character in DIGITS:
                tokens.append(self.make_token_number())
            elif self.current_character in LETTERS:
                tokens.append(self.make_token_identifier())
            elif self.current_character == '"':
                tokens.append(self.make_token_string())
            elif self.current_character == '+':
                tokens.append(Token(PLUS, start_position=self.position))
                self.next_character()
            elif self.current_character == '-':
                tokens.append(self.make_token_minus_or_arrow())
            elif self.current_character == '*':
                tokens.append(Token(MUL, start_position=self.position))
                self.next_character()
            elif self.current_character == '/':
                tokens.append(Token(DIV, start_position=self.position))
                self.next_character()
            else:
                start_position = self.position.copy_position()
                char = self.current_character
                self.next_character()
                return [], IllegalCharError(start_position, self.position, "'" + char + "'")

        tokens.append(Token(EOF, start_position=self.position))

        return tokens, None

    def make_token_identifier(self):
        id_str = ''
        start_position = self.position.copy_position()

        while self.current_character != None and self.current_character in LETTERS_DIGITS + '_':
            id_str += self.current_character
            self.next_character()

        if id_str in KEYWORDS:
            token_type = KEYWORD
        else:
            token_type = IDENTIFIER
        return Token(token_type, id_str, start_position, self.position)

    def make_token_minus_or_arrow(self):
        token_type = MINUS
        start_position = self.position.copy_position()
        self.next_character()

        if self.current_character == '>':
            self.next_character()
            token_type = ARROW

        return Token(token_type, start_position=start_position, end_position=self.position)

    def make_token_equals(self):
        token_type = EQ
        start_position = self.position.copy_position()
        self.next_character()

        if self.current_character == '=':
            self.next_character()
            token_type = EE

        return Token(token_type, start_position=start_position, end_position=self.position)

    def make_token_not_equals(self):
        start_position = self.position.copy_position()
        self.next_character()

        if self.current_character == '=':
            self.next_character()
            return Token(NE, start_position=start_position, end_position=self.position), None

        self.next_character()
        return None, ExpectedCharError(start_position, self.position, "'=' (after '!')")

    def make_token_greater_than(self):
        token_type = GT
        start_position = self.position.copy_position()
        self.next_character()

        if self.current_character == '=':
            self.next_character()
            token_type = GTE

        return Token(token_type, start_position=start_position, end_position=self.position)

    def make_token_less_than(self):
        token_type = LT
        start_position = self.position.copy_position()
        self.next_character()

        if self.current_character == '=':
            self.next_character()
            token_type = LTE

        return Token(token_type, start_position=start_position, end_position=self.position)

    def skip_comment(self):
        self.next_character()

        while self.current_character != '\n':
            self.next_character()

        self.next_character()

    def make_token_number(self):
        number_string = ''
        dot_count = 0
        start_position = self.position.copy_position()

        while self.current_character != None and self.current_character in DIGITS + '.':
            if self.current_character == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            number_string += self.current_character
            self.next_character()

        if dot_count == 0:
            return Token(INT, int(number_string), start_position, self.position)
        else:
            return Token(FLOAT, float(number_string), start_position, self.position)

    def make_token_string(self):
        string = ''
        start_position = self.position.copy_position()
        escape_character = False
        self.next_character()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_character != None and (self.current_character != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_character, self.current_character)
            else:
                if self.current_character == '\\':
                    escape_character = True
                else:
                    string += self.current_character
            self.next_character()
            escape_character = False

        self.next_character()
        return Token(STRING, string, start_position, self.position)