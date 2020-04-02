
from .token import *


def parse(lexemes):
    bp = BNFParser()
    rules = bp.parse(lexemes)
    return rules, bp.get_nt_map()


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

    def _eval(self, op: Token):
        """
        Helper for evaluating subsitution of a production rule.
        """
        if not self.vstack:
            raise BNFSyntaxError(f"missing operand for operator", op.pos)
        rhs = self.vstack.pop()

        if op.name == OPERATOR_RE_CONCATENATION:
            if not self.vstack:
                raise BNFSyntaxError(
                    f"missing operand for operator", op.pos)
            lhs = self.vstack.pop()
            lhs.extend(rhs)
            self.vstack.append(lhs)
        elif op.name == OPERATOR_RE_ALTERNATION:
            res = self._alloc_nt()
            if not self.vstack:
                raise BNFSyntaxError(
                    f"missing operand for operator", op.pos)
            lhs = self.vstack.pop()
            self.rules.append((res, rhs))
            self.rules.append((res, lhs))
            self.vstack.append([res])
        elif op.name == OPERATOR_RE_ZERO_OR_MORE:
            res = self._alloc_nt()
            self.rules.append((res, rhs + [res]))
            self.rules.append((res, [""]))
            self.vstack.append([res])
        elif op.name == OPERATOR_RE_ONE_OR_MORE:
            res = self._alloc_nt()
            self.rules.append((res, rhs + [res]))
            self.rules.append((res, rhs))
            self.vstack.append([res])
        elif op.name == OPERATOR_RE_ZERO_OR_ONE:
            res = self._alloc_nt()
            self.rules.append((res, rhs))
            self.rules.append((res, [""]))
            self.vstack.append([res])
        else:
            raise Exception(f"parser error: unexpected operator {op.name}")

    def parse(self, lexemes):
        """
        Parse lexemes into production rules.
        """

        while len(lexemes) > 0:
            if len(lexemes) < 3:
                raise BNFSyntaxError("cannot form a rule", lexemes[-1].pos)
            if lexemes[0].name != NON_TERMINAL:
                raise BNFSyntaxError(
                    "beginning of a rule is not non-terminal", lexemes[0].pos)
            if lexemes[1].name != OPREATOR_ASSIGNMENT:
                raise BNFSyntaxError(
                    "expect assignment operator after non-terminal", lexemes[1].pos)

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
                raise BNFSyntaxError(
                    "rule for this non-terminal has no subsitution part", nt.pos)

            # evaluate/expand the subsitution part
            nt_idx = self._alloc_nt(nt.value)
            is_last_tk_v = False

            for tk in sub:
                if tk.name == PRECENDENCE_OVERRIDE_BEGIN:
                    self.opstack.append(tk)
                    is_last_tk_v = False
                elif tk.name == PRECENDENCE_OVERRIDE_END:
                    last_op = Token(-1, "", i)
                    while self.opstack:
                        last_op = self.opstack.pop()
                        if last_op.name == PRECENDENCE_OVERRIDE_BEGIN:
                            break
                        self._eval(last_op)
                    if last_op.name != PRECENDENCE_OVERRIDE_BEGIN:
                        raise BNFSyntaxError("missing )", tk.pos)
                elif tk.name == OPERATOR_RE_ZERO_OR_MORE:
                    self.opstack.append(tk)
                elif tk.name == OPERATOR_RE_ONE_OR_MORE:
                    self.opstack.append(tk)
                elif tk.name == OPERATOR_RE_ZERO_OR_ONE:
                    self.opstack.append(tk)
                elif tk.name == OPERATOR_RE_ALTERNATION:
                    while self.opstack:
                        top = self.opstack[-1]
                        if top.name in (OPERATOR_RE_ZERO_OR_MORE, OPERATOR_RE_ONE_OR_MORE, OPERATOR_RE_ZERO_OR_ONE, OPERATOR_RE_CONCATENATION):
                            self._eval(top)
                            self.opstack.pop()
                        else:
                            break
                    self.opstack.append(tk)
                    is_last_tk_v = False
                elif tk.name == NON_TERMINAL or tk.name == TERMINAL:
                    v = tk.value
                    if tk.name == NON_TERMINAL:
                        v = self._alloc_nt(v)
                    if is_last_tk_v:
                        while self.opstack:
                            top = self.opstack[-1]
                            if top.name in (OPERATOR_RE_ZERO_OR_MORE, OPERATOR_RE_ONE_OR_MORE, OPERATOR_RE_ZERO_OR_ONE):
                                self._eval(top)
                                self.opstack.pop()
                            else:
                                break
                        self.opstack.append(
                            Token(OPERATOR_RE_CONCATENATION, '', tk.pos))
                    self.vstack.append([v])
                    is_last_tk_v = True
                else:
                    raise Exception(
                        f"parser error: got unexpected token type {tk.name}")
            while self.opstack:
                op = self.opstack.pop()
                if op.name == PRECENDENCE_OVERRIDE_BEGIN:
                    raise BNFSyntaxError("missing )", op.pos)
                self._eval(op)

            self.rules.append((nt_idx, self.vstack.pop()))

        self.rules.sort(key=lambda x: x[0], reverse=True)
        return self.rules

    def get_nt_map(self):
        """
        Get the index-to-name mapping for non-terminals.
        """
        return {v: k for k, v in self.nt_map.items()}

    def check_warnings(self):
        """
        Check for warnings.
        """

        warning_msg = []

        # unproducible non-terminals
        nt_map = self.get_nt_map()
        all_nt = set()
        producible_nt = set()
        for nt, sub in self.rules:
            producible_nt.add(nt)
            for a in sub:
                if type(a) is int:
                    all_nt.add(a)
        for nt in all_nt - producible_nt:
            warning_msg.append(
                f"warning: no production rule for <{nt_map[nt]}> ({nt})")

        return warning_msg
