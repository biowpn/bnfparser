
from .token import *

import argparse
import string


def lex(_input, long: False):

    lexemes = []

    sl_char = ''
    word = ""

    for _, c in enumerate(_input):
        if sl_char == r'"' or sl_char == r"'":
            if c == sl_char:
                if word == "" or long:
                    lexemes.append(Token(TERMINAL, word))
                else:
                    for a in word:
                        lexemes.append(Token(TERMINAL, a))
                word = ""
                sl_char = ''
            else:
                word += c
            continue

        elif sl_char == r'<':
            if c == '>':
                if word == "":
                    raise Exception(f"non-terminal identifier is empty")
                lexemes.append(Token(NON_TERMINAL, word))
                word = ""
                sl_char = ''
            else:
                word += c
            continue

        elif sl_char == '%':
            if c in string.digits or c in string.ascii_letters:
                word += c
                continue
            if len(word) == 0:
                raise Exception(f"no numeric expression after {sl_char}")
            if word[0] == 'x':
                base = 16
                word = word[1:]
            elif word[0] == 'd':
                base = 10
                word = word[1:]
            elif word[0] == 'b':
                base = 2
                word = word[1:]
            elif word[0] in string.digits:
                base = 10
            else:
                raise Exception(
                    f"unknown base specifier for numeric expression: {word[0]}")
            lexemes.append(Token(TERMINAL, chr(int(word, base))))
            sl_char = ''
            word = ""

        elif sl_char != '':
            raise Exception(f"lexer error: unexpected slc {sl_char}")

        if c == r'"' or c == r"'":
            sl_char = c

        elif c == '<':
            word = ""
            sl_char = c

        elif c == '%':
            word = ""
            sl_char = c

        elif c == ':':
            word += c
        elif c == '=':
            lexemes.append(Token(OPREATOR_ASSIGNMENT, word + '='))
            word = ""

        elif c == '|':
            lexemes.append(Token(OPERATOR_RE_ALTERNATION, c))
        elif c == '*':
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_MORE, c))
        elif c == '+':
            lexemes.append(Token(OPERATOR_RE_ONE_OR_MORE, c))
        elif c == '?':
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_ONE, c))

        elif c == '[':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_BEGIN, c))
        elif c == ']':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_END, c))
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_ONE, c))

        elif c == '(':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_BEGIN, c))
        elif c == ')':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_END, c))

        elif c in string.whitespace:
            pass

        else:
            raise Exception(f"unexpected char '{c}''")

    return lexemes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType('r'),
                        help="path to bnf file to lex")
    parser.add_argument("-l", "--long", action="store_true",
                        help="preserve long terminals")
    args = parser.parse_args()

    print(*lex(args.file.read(), args.long), sep='\n')


if __name__ == "__main__":
    main()
