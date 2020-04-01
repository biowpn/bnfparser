
NON_TERMINAL = 1
TERMINAL = 2

OPREATOR_ASSIGNMENT = 3

PRECENDENCE_OVERRIDE_BEGIN = 6
PRECENDENCE_OVERRIDE_END = 7

OPERATOR_RE_ALTERNATION = 8
OPERATOR_RE_ZERO_OR_MORE = 9
OPERATOR_RE_ONE_OR_MORE = 10
OPERATOR_RE_ZERO_OR_ONE = 11


class Token:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    # for debug
    def __repr__(self):
        return f"Token({self.name}, {repr(self.value)})"
