
import argparse
import json
import sys

from . import lexer
from . import parser


def translate(rules, nt_map):

    translated = []
    for nt, sub in rules:
        nt_named = f"<{nt_map[nt]}>"
        sub_named = []
        for a in sub:
            if type(a) is int:
                a = f"<{nt_map[a]}>"
            else:
                a = repr(a)
            sub_named.append(a)
        translated.append((nt_named, sub_named))
    return translated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=argparse.FileType('r'),
                    help="BNF syntax file")
    ap.add_argument("-l", "--long", action="store_true",
                    help="preserve long terminals")
    ap.add_argument("-v", "--verify", action="store_true",
                    help="only verify whether the syntax is correct instead of printing out each rule")
    ap.add_argument("-t", "--translate", action="store_true",
                    help="translate non-terminals (represented by an integer) to their origin names")
    ap.add_argument("-f", "--format", choices=["raw", "bnf", "json"], default="raw",
                    help="output format")
    ap.add_argument("-o", "--out", type=argparse.FileType('w'), default=sys.stdout,
                    help="output file")
    args = ap.parse_args()

    bp = parser.BNFParser()

    buf = args.file.read()

    try:
        lexemes = lexer.lex(buf, args.long)
        rules = bp.parse(lexemes)
    except parser.ParsingException as e:
        print(f"syntax error: {e}")
        return

    if args.verify:
        print("syntax correct")
        return

    if args.translate:
        rules = translate(rules, bp.get_nt_map())

    if args.format == "raw":
        for rule in rules:
            print(rule, file=args.out)
    elif args.format == "bnf":
        for nt, sub in rules:
            print(nt, "::=", *sub, file=args.out)
    elif args.format == "json":
        json.dump(rules, args.out, indent=4)


if __name__ == "__main__":
    main()
