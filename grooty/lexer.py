from enum import Enum
import sys

EOF = '\0'

class TokenSymbols(Enum):
    PLUS = '+'
    MINUS = '-'


class TokenType(Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

    # Keywords:
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # Operators:
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:
    def __init__(self, token_text, token_type):
        self.text = token_text
        self.type = token_type

    @staticmethod
    def check_if_keyword(keyword):
        for kind in TokenType:
            if kind.name == keyword and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class Lexer:

    def __init__(self, source: str):
        self.source = source
        self.current_char = ''
        self.current_pos = -1
        self.next()

    def next(self):
        self.current_pos += 1
        if self.current_pos >= len(self.source):
            self.current_char = EOF
        else:
            self.current_char = self.source[self.current_pos]

    def peek(self):
        if self.current_pos + 1 > len(self.source):
            return EOF
        return self.source[self.current_pos + 1]

    def abort(self, message):
        sys.exit(f"Lexing error: {message}")

    def skip_whitespace(self):
        while self.current_char == ' ' or self.current_char == '\t' or self.current_char == '\r':
            self.next()

    def skip_comments(self):
        if self.current_char == '#':
            while self.current_char != '\n':
                self.next()

    def get_token(self):
        self.skip_whitespace()
        self.skip_comments()
        token = None

        match self.current_char:
            case '+':
                token = Token(self.current_char, TokenType.PLUS)
            case '-':
                token = Token(self.current_char, TokenType.MINUS)
            case '*':
                token = Token(self.current_char, TokenType.ASTERISK)
            case '/':
                token = Token(self.current_char, TokenType.SLASH)
            case '=':
                if self.peek() == '=':
                    last_char = self.current_char
                    self.next()
                    token = Token(last_char + self.current_char, TokenType.EQEQ)
                else:
                    token = Token(self.current_char, TokenType.EQ)
            case '>':
                if self.peek() == '=':
                    last_char = self.current_char
                    self.next()
                    token = Token(last_char + self.current_char, TokenType.GTEQ)
                else:
                    token = Token(self.current_char, TokenType.GT)
            case '<':
                if self.peek() == '=':
                    last_char = self.current_char
                    self.next()
                    token = Token(last_char + self.current_char, TokenType.LTEQ)
                else:
                    token = Token(self.current_char, TokenType.LT)
            case '!':
                if self.peek() == '=':
                    last_char = self.current_char
                    self.next()
                    token = Token(last_char + self.current_char, TokenType.NOTEQ)
                else:
                    self.abort(f"Expected !=, got !{self.peek()}")
            case '\"':
                self.next()
                start_pos = self.current_pos
                while self.current_char != '\"':
                    if self.current_char in ['\r', '\n', '\t', '\\', '%']:
                        self.abort(f"Illegal character in string {self.current_char}")
                    self.next()
                text = self.source[start_pos:self.current_pos]
                token = Token(text, TokenType.STRING)
            case _ if self.current_char.isdigit():
                start_pos = self.current_pos
                while self.peek().isdigit():
                    self.next()
                if self.peek() == '.':  # float?
                    self.next()

                    if not self.peek().isdigit():
                        self.abort(f"Illegal character in number sequence \
                                {self.source[start_pos:self.current_pos]}")
                    while self.peek().isdigit():
                        self.next()

                number = self.source[start_pos:self.current_pos + 1]
                token = Token(number, TokenType.NUMBER)
            case _ if self.current_char.isalpha():
                start_pos = self.current_pos
                while self.peek().isalpha():
                    self.next()
                text = self.source[start_pos:self.current_pos + 1]
                keyword = Token.check_if_keyword(text)
                token = Token(text, keyword if keyword else TokenType.IDENT)

            case '\n':
                token = Token(self.current_char, TokenType.NEWLINE)
            case '\0':
                token = Token(self.current_char, TokenType.EOF)
            case _:
                self.abort(f"Unknown token {self.current_char}")

        self.next()
        return token




if __name__ == '__main__':
    source_token = "IF+-123 foo*THEN/"

    lexer = Lexer(source_token)
    token = lexer.get_token()
    i = 0
    while token.type != TokenType.EOF:
        print(i, token.type)
        token = lexer.get_token()
        i += 1

        

