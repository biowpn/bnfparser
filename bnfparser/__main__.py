
import argparse
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
    ap.add_argument("-t", "--translate", action="store_true",
                    help="translate non-terminals to their origin names")
    ap.add_argument("-f", "--format", choices=["raw", "bnf", "ssi"], default="raw",
                    help="output format")
    ap.add_argument("-o", "--out", type=argparse.FileType('w'), default=sys.stdout,
                    help="output file")
    ap.add_argument('-W', "--warning", action="store_true",
                    help="issue warnings")
    args = ap.parse_args()

    bp = parser.BNFParser()

    buf = args.file.read()

    try:
        lexemes = lexer.lex(buf, args.long)
        rules = bp.parse(lexemes)
    except parser.BNFSyntaxError as e:
        print(e.format(buf))
        return

    if args.translate:
        rules = translate(rules, bp.get_nt_map())

    if args.format == "raw":
        for rule in rules:
            print(rule, file=args.out)
    elif args.format == "bnf":
        for nt, sub in rules:
            print(nt, "::=", *sub, file=args.out)
    elif args.format == "ssi":
        for nt, sub in rules:
            ints = []
            for a in sub:
                if type(a) is int:
                    ints.append(a)
                elif a == "":
                    ints.append(0)
                else:
                    ints.append(ord(a))
            print(nt, *ints, file=args.out)

    if args.warning:
        print(*bp.check_warnings(), sep='\n')


if __name__ == "__main__":
    main()
