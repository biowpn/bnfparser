
import argparse
import json
import sys

from . import bnfparser


def translate(rules, nt_map):

    def get_nt_name(nt):
        if nt in nt_map:
            return '<' + nt_map[nt] + '>'
        else:
            return '<(temp-{})>'.format(nt)

    translated = []
    for nt, sub in rules:
        nt_named = get_nt_name(nt)
        sub_named = []
        for a in sub:
            if type(a) is int:
                a = get_nt_name(a)
            else:
                a = repr(a)
            sub_named.append(a)
        translated.append((nt_named, sub_named))
    return translated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType('r'),
                        help="BNF syntax file")
    parser.add_argument("-l", "--long", action="store_true",
                        help="preserve long terminals")
    parser.add_argument("-v", "--verify", action="store_true",
                        help="only verify whether the syntax is correct instead of printing out each rule")
    parser.add_argument("-t", "--translate", action="store_true",
                        help="translate non-terminals (represented by an integer) to their origin names")
    parser.add_argument("-f", "--format", choices=["bnf", "json"], default="bnf",
                        help="output format")
    parser.add_argument("-o", "--out", type=argparse.FileType('w'), default=sys.stdout,
                        help="output file")
    args = parser.parse_args()

    buf = args.file.read()

    try:
        rules, nt_map = bnfparser.parse(buf, args.long)
    except bnfparser.ParsingException as e:
        print("syntax error:")
        print(str(e))
        return

    if args.verify:
        print("syntax correct")
        return

    if args.translate:
        reverse_nt_map = {v: k for k, v in nt_map.items()}
        rules = translate(rules, reverse_nt_map)

    if args.format == "bnf":
        for nt, sub in rules:
            print(nt, "::=", *sub, file=args.out)
    elif args.format == "json":
        json.dump(rules, args.out, indent=4)


if __name__ == "__main__":
    main()
