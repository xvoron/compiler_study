"""
Grammar:

program ::= {statement}
statement ::= "PRINT" (expression | string) nl
    | "LET" ident "=" expression nl
    | "IF" comparison "THEN" nl {statement} "END" nl
    | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
    | "LABEL" ident nl
    | "GOTO" ident nl
    | "INPUT" ident nl
comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)
expression ::= term {("-" | "+") term}
term ::= unary {("/" | "*") unary}
unary ::= ["+" | "-"] primary
primary ::= number | ident
nl ::= "\n"+

Notation:
    {} - zero or more
    [] - zero or one
    + - one or more
    () - grouping
    | - logical or
"""

from functools import wraps
import sys
from typing import Optional

from lexer import Lexer, Token, TokenType
from emitter import Emitter


def assert_token_none(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        assert self.current_token is not None, "Error: current token is None"
        return func(self, *args, **kwargs)
    return wrapper


class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter):
        self._lexer = lexer
        self._emitter = emitter

        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()


        self.current_token: Optional[Token] = None
        self.peek_token = None

        self.next_token()
        self.next_token()

    def check_token(self, type_: TokenType) -> bool:
        """Return true if the current token matches."""
        assert self.current_token is not None, "Error: current token is None"
        return type_ == self.current_token.type

    def check_peek(self, type_: TokenType) -> bool:
        """Return true if the next token matches."""
        assert self.current_token is not None, "Error: current token is None"
        return type_ == self.current_token.type


    def match(self, type_: TokenType):
        """Try to match current token (if not, error)."""
        assert self.current_token is not None, "Error: current token is None"
        if not self.check_token(type_):
            self.abort(f"Expected {type_.name}, got {self.current_token.type}")
        self.next_token()

    def next_token(self):
        self.current_token = self.peek_token
        self.peek_token = self._lexer.get_token()

    def abort(self, message: str):
        sys.exit(f"Error: {message}")


    def program(self):
        """program ::= {statement}"""
        self._emitter.header_line("#include <stdio.h>")
        self._emitter.header_line("int main(void){")

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        while not self.check_token(TokenType.EOF):
            self.statement()

        self._emitter.emit_line("return 0;")
        self._emitter.emit_line("}")

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort(f"Attempting to GOT to undeclared label: {label}")

    def statement(self):
        """
        statement ::= "PRINT" (expression | string) nl
            | "LET" ident "=" expression nl
            | "IF" comparison "THEN" nl {statement} "END" nl
            | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
            | "LABEL" ident nl
            | "GOTO" ident nl
            | "INPUT" ident nl
        """
        assert self.current_token is not None, "Error: current token is None"

        if self.check_token(TokenType.PRINT):
            self.next_token()
            if self.check_token(TokenType.STRING):
                self._emitter.emit_line(f"printf(\"{self.current_token.text}\\n\");")
                self.next_token()
            else:
                self._emitter.emit("printf(\"%.2f\\n\", (float)(")
                self.expression()
                self._emitter.emit_line("));")

        elif self.check_token(TokenType.IF):
            self.next_token()

            self._emitter.emit("if(")

            self.comparison()
            self.match(TokenType.THEN)

            self.nl()
            self._emitter.emit_line("){")

            while not self.check_token(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)

            self._emitter.emit_line("}")

        elif self.check_token(TokenType.WHILE):
            self.next_token()

            self._emitter.emit("while(")

            self.comparison()
            self.match(TokenType.REPEAT)
            self.nl()

            self._emitter.emit_line("){")

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)

            self._emitter.emit_line("}")

        elif self.check_token(TokenType.LET):
            self.next_token()

            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)

                self._emitter.header_line(f"float {self.current_token.text};")

            self._emitter.emit(self.current_token.text + " = ")

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()

            self._emitter.emit_line(";")

        elif self.check_token(TokenType.LABEL):
            self.next_token()

            if self.current_token in self.labels_declared:
                self.abort(f"Label already exists: {self.current_token.text}")
            self.labels_declared.add(self.current_token.text)

            self._emitter.emit_line(self.current_token.text + ":")

            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.GOTO):
            self.next_token()
            self.labels_gotoed.add(self.current_token.text)
            
            self._emitter.emit_line(f"goto {self.current_token.text};")

            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.INPUT):
            self.next_token()

            if self.current_token.text not in self.symbols:
                self.symbols.add(self.current_token.text)
                self._emitter.header_line(f"float {self.current_token.text};")
            
            self._emitter.emit_line(f"(if(0 == scanf(\"%f\", &{self.current_token.text})) {{")
            self._emitter.emit_line(self.current_token.text + " = 0;")
            self._emitter.emit("scanf(\"%")
            self._emitter.emit_line("*s\");")
            self._emitter.emit_line("}")

            self.match(TokenType.IDENT)

        else:
            assert self.current_token is not None, "Error: current token is None"
            self.abort(f"Invalid statement at {self.current_token.text} ({self.current_token.type.name})")

        self.nl()

    def comparison(self):
        """
        comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)
        """
        ...
        assert self.current_token is not None, "Error: current token is None"
        self.expression()

        # Must be at least one operator and another expression
        if self._is_comparison_operator():

            self._emitter.emit(self.current_token.text)

            self.next_token()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.current_token}")

        while self._is_comparison_operator():

            self._emitter.emit(self.current_token.text)

            self.next_token()
            self.expression()


    def expression(self):
        """
        expression ::= term {("-" | "+") term}
        """
        assert self.current_token is not None, "Error: current token is None"

        self.term()
        # 0 or more
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):

            self._emitter.emit(self.current_token.text)

            self.next_token()
            self.term()

    def term(self):
        """
        term ::= unary {("/" | "*") unary}
        """
        assert self.current_token is not None, "Error: current token is None"

        self.unary()
        while self.check_token(TokenType.SLASH) or self.check_token(TokenType.ASTERISK):

            self._emitter.emit(self.current_token.text)

            self.next_token()
            self.unary()

    def unary(self):
        """
        unary ::= ["+" | "-"] primary
        """
        assert self.current_token is not None, "Error: current token is None"

        # Optional 0 or 1
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):

            self._emitter.emit(self.current_token.text)

            self.next_token()

        self.primary()


    def primary(self):
        """
        primary ::= number | ident
        """
        assert self.current_token is not None, "Error: current token is None"

        if self.check_token(TokenType.NUMBER):

            self._emitter.emit(self.current_token.text)

            self.next_token()
        elif self.check_token(TokenType.IDENT):
            if self.current_token.text not in self.symbols:
                self.abort(f"Referencing variable before assignment: {self.current_token.text}")

            self._emitter.emit(self.current_token.text)

            self.next_token()
        else:
            self.abort(f"Unexpected token at {self.current_token.text}")
        

    def nl(self):
        """nl ::= "\n"+"""
        self.match(TokenType.NEWLINE)

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    def _is_comparison_operator(self):
        return self.check_token(TokenType.EQEQ) or \
               self.check_token(TokenType.NOTEQ) or \
               self.check_token(TokenType.GT) or \
               self.check_token(TokenType.LT) or \
               self.check_token(TokenType.GTEQ) or \
               self.check_token(TokenType.LTEQ)
