
from .token import *


class ParsingException(Exception):

    def __init__(self, desc, line, col):
        self.desc = desc
        self.line = line
        self.col = col

    def __str__(self):
        return f"line {self.line}, column {self.col}: {self.desc}"


class BNFParser:

    def __init__(self):
        self.nt_map = {}
        self.nt_count = 0

        self.vstack = []
        self.opstack = []

        self.rules = []

    def _alloc_nt(self, name=None):
        """
        Index a non-terminal by its name.
        If the non-terminal has been indexed before, its existing index will be returned.
        If `name` is None, a new index will be allocated to the non-terminal and it'll be named like "temp-%d".
        """
        if name not in self.nt_map:
            self.nt_count += 1
            if name is None:
                name = f"temp-{self.nt_count}"
            self.nt_map[name] = -self.nt_count
        return self.nt_map[name]

    def _eval(self, op: int):
        """
        Helper for evaluating subsitution of a production rule.
        """
        res = self._alloc_nt()
        lhs = self.vstack.pop()
        if op == OPERATOR_RE_ALTERNATION:
            rhs = self.vstack.pop()
            self.rules.append((res, lhs))
            self.rules.append((res, rhs))
        elif op == OPERATOR_RE_ZERO_OR_MORE:
            self.rules.append((res, lhs + [res]))
            self.rules.append((res, [""]))
        elif op == OPERATOR_RE_ONE_OR_MORE:
            self.rules.append((res, lhs + [res]))
            self.rules.append((res, lhs))
        elif op == OPERATOR_RE_ZERO_OR_ONE:
            self.rules.append((res, lhs))
            self.rules.append((res, [""]))
        else:
            raise Exception(f"unknown operator {op}")
        self.vstack.append([res])

    def parse(self, lexemes):
        """
        Parse lexemes into production rules.
        """

        while len(lexemes) > 0:
            if len(lexemes) < 3:
                raise Exception("too few lexemes to form a rule")
            if lexemes[0].name != NON_TERMINAL:
                raise Exception("beginning of a rule is not non-terminal")
            if lexemes[1].name != OPREATOR_ASSIGNMENT:
                raise Exception(
                    "missing assignment operator after non-terminal")

            # extract a production rule
            i = 2
            while i < len(lexemes):
                if lexemes[i].name == OPREATOR_ASSIGNMENT:
                    i -= 1
                    break
                i += 1
            nt = lexemes[0]
            sub = lexemes[2: i]
            lexemes = lexemes[i:]
            if len(sub) == 0:
                raise Exception("subsitution part is empty for rule")

            # evaluate/expand the subsitution part
            nt_idx = self._alloc_nt(nt.value)
            is_last_tk_v = False

            for tk in sub:
                is_cur_tk_v = False
                if tk.name == PRECENDENCE_OVERRIDE_BEGIN:
                    self.opstack.append(PRECENDENCE_OVERRIDE_BEGIN)
                elif tk.name == PRECENDENCE_OVERRIDE_END:
                    last_op = self.opstack.pop()
                    while last_op != PRECENDENCE_OVERRIDE_BEGIN:
                        self._eval(last_op)
                        last_op = self.opstack.pop()
                elif tk.name == OPERATOR_RE_ZERO_OR_MORE:
                    self.opstack.append(tk.name)
                elif tk.name == OPERATOR_RE_ONE_OR_MORE:
                    self.opstack.append(tk.name)
                elif tk.name == OPERATOR_RE_ZERO_OR_ONE:
                    self.opstack.append(tk.name)
                elif tk.name == OPERATOR_RE_ALTERNATION:
                    while self.opstack:
                        top = self.opstack[-1]
                        if top == PRECENDENCE_OVERRIDE_BEGIN or top == OPERATOR_RE_ALTERNATION:
                            break
                        self._eval(top)
                        self.opstack.pop()
                    self.opstack.append(tk.name)
                elif tk.name == NON_TERMINAL:
                    is_cur_tk_v = True
                    _i = self._alloc_nt(tk.value)
                    if is_last_tk_v:
                        self.vstack[-1].append(_i)
                    else:
                        self.vstack.append([_i])
                elif tk.name == TERMINAL:
                    is_cur_tk_v = True
                    if is_last_tk_v:
                        self.vstack[-1].append(tk.value)
                    else:
                        self.vstack.append([tk.value])
                else:
                    raise Exception(f"got unexpected token type {tk.name}")
                is_last_tk_v = is_cur_tk_v
            while self.opstack:
                self._eval(self.opstack.pop())

            self.rules.append((nt_idx, self.vstack.pop()))

        return self.rules

    def get_nt_map(self):
        """
        Get the index-to-name mapping for non-terminals.
        """
        return {v: k for k, v in self.nt_map.items()}
