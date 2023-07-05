from lexer import Lexer
from parser import Parser
from emitter import Emitter
import sys


def main():
    print("Groovy Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: No source code provided.")

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()
    emitter.write_file()
    print("Parsing completed.")


if __name__ == '__main__':
    main()
