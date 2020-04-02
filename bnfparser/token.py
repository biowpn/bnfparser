
NON_TERMINAL = 1
TERMINAL = 2

OPREATOR_ASSIGNMENT = 3

PRECENDENCE_OVERRIDE_BEGIN = 6
PRECENDENCE_OVERRIDE_END = 7

OPERATOR_RE_CONCATENATION = 8
OPERATOR_RE_ALTERNATION = 9
OPERATOR_RE_ZERO_OR_MORE = 10
OPERATOR_RE_ONE_OR_MORE = 11
OPERATOR_RE_ZERO_OR_ONE = 12


class Token:

    def __init__(self, name, value, pos):
        self.name = name
        self.value = value
        self.pos = pos

    # for debug
    def __repr__(self):
        return f"Token({self.name}, {repr(self.value)})"


class BNFSyntaxError(Exception):

    def __init__(self, desc, pos):
        self.desc = desc
        self.pos = pos

    def __str__(self):
        return f"ParsingException(\"{self.desc}\", {self.pos}"

    def format(self, _input):
        pos = self.pos
        fulldesc = ""
        for i, line in enumerate(_input.split('\n')):
            if pos >= len(line) + 1:
                pos -= len(line) + 1
                continue
            line_prefix = f"line {i + 1}: "
            fulldesc += f"{line_prefix}{line}\n"
            fulldesc += ' ' * (len(line_prefix) + pos) + '^' + '\n'
            fulldesc += f"syntax error: {self.desc}"
            break
        return fulldesc
