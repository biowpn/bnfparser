
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

        rhs = self.vstack.pop()
        if op == OPERATOR_RE_CONCATENATION:
            lhs = self.vstack.pop()
            lhs.extend(rhs)
            self.vstack.append(lhs)
        elif op == OPERATOR_RE_ALTERNATION:
            res = self._alloc_nt()
            lhs = self.vstack.pop()
            self.rules.append((res, rhs))
            self.rules.append((res, lhs))
            self.vstack.append([res])
        elif op == OPERATOR_RE_ZERO_OR_MORE:
            res = self._alloc_nt()
            self.rules.append((res, rhs + [res]))
            self.rules.append((res, [""]))
            self.vstack.append([res])
        elif op == OPERATOR_RE_ONE_OR_MORE:
            res = self._alloc_nt()
            self.rules.append((res, rhs + [res]))
            self.rules.append((res, rhs))
            self.vstack.append([res])
        elif op == OPERATOR_RE_ZERO_OR_ONE:
            res = self._alloc_nt()
            self.rules.append((res, rhs))
            self.rules.append((res, [""]))
            self.vstack.append([res])
        else:
            raise Exception(f"unknown operator {op}")

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
                if tk.name == PRECENDENCE_OVERRIDE_BEGIN:
                    self.opstack.append(PRECENDENCE_OVERRIDE_BEGIN)
                    is_last_tk_v = False
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
                        if top in (OPERATOR_RE_ZERO_OR_MORE, OPERATOR_RE_ONE_OR_MORE, OPERATOR_RE_ZERO_OR_ONE, OPERATOR_RE_CONCATENATION):
                            self._eval(top)
                            self.opstack.pop()
                        else:
                            break
                    self.opstack.append(tk.name)
                    is_last_tk_v = False
                elif tk.name == NON_TERMINAL or tk.name == TERMINAL:
                    v = tk.value
                    if tk.name == NON_TERMINAL:
                        v = self._alloc_nt(v)
                    if is_last_tk_v:
                        while self.opstack:
                            top = self.opstack[-1]
                            if top in (OPERATOR_RE_ZERO_OR_MORE, OPERATOR_RE_ONE_OR_MORE, OPERATOR_RE_ZERO_OR_ONE):
                                self._eval(top)
                                self.opstack.pop()
                            else:
                                break
                        self.opstack.append(OPERATOR_RE_CONCATENATION)
                    self.vstack.append([v])
                    is_last_tk_v = True
                else:
                    raise Exception(f"got unexpected token type {tk.name}")
            while self.opstack:
                self._eval(self.opstack.pop())

            self.rules.append((nt_idx, self.vstack.pop()))

        return self.rules

    def get_nt_map(self):
        """
        Get the index-to-name mapping for non-terminals.
        """
        return {v: k for k, v in self.nt_map.items()}
