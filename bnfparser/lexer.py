
from .token import *

import argparse
import string


def lex(_input, long: False):

    lexemes = []

    sl_char = ''
    word = ""

    for i, c in enumerate(_input):
        if sl_char == r'"' or sl_char == r"'":
            if c == sl_char:
                if word == "" or long:
                    lexemes.append(Token(TERMINAL, word, i - 1))
                else:
                    for a in word:
                        lexemes.append(Token(TERMINAL, a, i - 1))
                word = ""
                sl_char = ''
            else:
                word += c
            continue

        elif sl_char == r'<':
            if c == '>':
                if word == "":
                    raise BNFSyntaxError(
                        f"missing non-terminal identifier", i)
                lexemes.append(Token(NON_TERMINAL, word, i - 1))
                word = ""
                sl_char = ''
            elif c in string.ascii_letters or c in string.digits or c == '-' or c == '_' or c == ' ':
                word += c
            else:
                raise BNFSyntaxError(
                    f"invalid character for non-terminal identifier", i)
            continue

        elif sl_char == '%':
            if c in string.digits or c in string.ascii_letters:
                word += c
                continue
            if len(word) == 0:
                raise BNFSyntaxError(
                    f"no numeric expression after {sl_char}", i)
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
                raise BNFSyntaxError(
                    f"unknown base specifier for numeric expression", i - len(word))
            try:
                a = chr(int(word, base))
            except ValueError as e:
                raise BNFSyntaxError(
                    f"invalid numeric expression: {e}", i - len(word))
            lexemes.append(Token(TERMINAL, a, i - 1))
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
            lexemes.append(Token(OPREATOR_ASSIGNMENT, word + '=', i))
            word = ""

        elif c == '|':
            lexemes.append(Token(OPERATOR_RE_ALTERNATION, c, i))
        elif c == '*':
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_MORE, c, i))
        elif c == '+':
            lexemes.append(Token(OPERATOR_RE_ONE_OR_MORE, c, i))
        elif c == '?':
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_ONE, c, i))

        elif c == '[':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_BEGIN, c, i))
        elif c == ']':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_END, c, i))
            lexemes.append(Token(OPERATOR_RE_ZERO_OR_ONE, c, i))

        elif c == '(':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_BEGIN, c, i))
        elif c == ')':
            lexemes.append(Token(PRECENDENCE_OVERRIDE_END, c, i))

        elif c in string.whitespace:
            pass

        else:
            raise BNFSyntaxError(f"unexpected character '{c}'", i)

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
