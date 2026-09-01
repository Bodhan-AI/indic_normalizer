"""Recursive-descent parser turning a token stream into an expression tree.

Never raises on malformed input: unexpected tokens are skipped, unmatched
delimiters are closed at end of input.
"""

from __future__ import annotations

from .lexer import tokenize
from . import symbols as S


# --------------------------------------------------------------------------
# Node model
# --------------------------------------------------------------------------
class Node:
    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)

    def __repr__(self):  # pragma: no cover - debug helper
        d = {k: v for k, v in self.__dict__.items() if k != "kind"}
        return "Node(%s, %r)" % (self.kind, d)


def Seq(items):
    return Node("seq", items=[x for x in items if x is not None])


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.pos = 0

    # -- token cursor (skips SPACE tokens) --------------------------------
    def _idx(self):
        i = self.pos
        n = len(self.toks)
        while i < n and self.toks[i].type == "SPACE":
            i += 1
        return i

    def peek(self):
        i = self._idx()
        return self.toks[i] if i < len(self.toks) else None

    def advance(self):
        i = self._idx()
        tok = self.toks[i] if i < len(self.toks) else None
        self.pos = i + 1
        return tok

    # -- top level --------------------------------------------------------
    def parse(self):
        return self.parse_sequence()

    def parse_sequence(self, stop_types=(), stop_cmds=()):
        items = []
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type in stop_types:
                break
            if t.type == "COMMAND" and t.value in stop_cmds:
                break
            # Big operators greedily consume the remainder of the sequence
            # as their body.
            if t.type == "COMMAND" and t.value in S.BIGOPS:
                self.advance()
                node = self.parse_bigop(t.value)
                body = self.parse_sequence(stop_types, stop_cmds)
                if body.items:
                    node.body = body
                items.append(node)
                break
            node = self.parse_scripted(stop_types, stop_cmds)
            if node is not None:
                items.append(node)
        return Seq(items)

    # -- atoms with trailing scripts / application ------------------------
    def parse_scripted(self, stop_types=(), stop_cmds=()):
        base = self.parse_base(stop_types, stop_cmds)
        if base is None:
            return None

        # Function application: identifier immediately followed by "(...)"
        if base.kind == "ident":
            t = self.peek()
            if t is not None and t.type == "LPAREN":
                inner = self.parse_delim_chars("(", ")")
                base = Node("app", func=base, arg=inner)

        # Named function: optional power / subscript then an argument
        if base.kind == "func":
            while True:
                t = self.peek()
                if t is None:
                    break
                if t.type == "CARET":
                    self.advance()
                    base.power = self.parse_arg()
                elif t.type == "UNDERSCORE":
                    self.advance()
                    base.sub = self.parse_arg()
                else:
                    break
            if self._is_operand_start(stop_types, stop_cmds):
                base.arg = self.parse_scripted(stop_types, stop_cmds)
            return base

        # Superscript / subscript on a normal nucleus
        sup = sub = None
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type == "CARET":
                self.advance()
                sup = self.parse_arg()
            elif t.type == "UNDERSCORE":
                self.advance()
                sub = self.parse_arg()
            else:
                break
        if sup is not None or sub is not None:
            return Node("script", base=base, sup=sup, sub=sub)
        return base

    def _is_operand_start(self, stop_types=(), stop_cmds=()):
        t = self.peek()
        if t is None:
            return False
        if t.type in stop_types:
            return False
        if t.type in ("LBRACE", "LPAREN", "LBRACK"):
            return True
        if t.type == "CHAR":
            return t.value.isalnum() or t.value == "|"
        if t.type == "COMMAND":
            v = t.value
            if v in stop_cmds:
                return False
            return (
                v in S.GREEK
                or v in S.ACCENTS
                or v in S.FRAC_CMDS
                or v == "sqrt"
                or v in S.FUNCTIONS
                or v in S.TEXT_CMDS
                or v in S.OPERAND_SYMS
            )
        return False

    # -- a single argument (group or one atom) ----------------------------
    def parse_arg(self):
        t = self.peek()
        if t is None:
            return Seq([])
        if t.type == "LBRACE":
            self.advance()
            inner = self.parse_sequence(stop_types=("RBRACE",))
            if self.peek() is not None and self.peek().type == "RBRACE":
                self.advance()
            return inner
        # single-token argument: exactly one character/command (LaTeX rule).
        if t.type == "CHAR" and t.value.isdigit():
            self.advance()
            return Node("num", value=t.value)
        return self.parse_base()

    # -- bases ------------------------------------------------------------
    def parse_base(self, stop_types=(), stop_cmds=()):
        t = self.peek()
        if t is None:
            return None

        if t.type == "COMMAND":
            return self.parse_command(t.value)

        if t.type == "LBRACE":
            self.advance()
            inner = self.parse_sequence(stop_types=("RBRACE",))
            if self.peek() is not None and self.peek().type == "RBRACE":
                self.advance()
            return Node("group", body=inner)

        if t.type == "LPAREN":
            return self.parse_delim_chars("(", ")")
        if t.type == "LBRACK":
            return self.parse_delim_chars("[", "]")

        if t.type in ("RBRACE", "RPAREN", "RBRACK", "AMP", "DBACKSLASH"):
            # Unexpected closer: consume and skip.
            self.advance()
            return None

        if t.type == "CHAR":
            ch = t.value
            if ch.isdigit():
                return self.parse_number()
            if ch == "|":
                return self.parse_absval()
            if ch.isalpha():
                self.advance()
                return Node("ident", name=ch)
            self.advance()
            return Node("punct", value=ch)

        if t.type in ("CARET", "UNDERSCORE"):
            # Leading script with no base (e.g. ^\circ): use empty base.
            return Node("ident", name="")

        # Fallback
        self.advance()
        return None

    def parse_command(self, name):
        # Spacing macros -> dropped
        if name in S.SPACING:
            self.advance()
            return None

        self.advance()

        if name in S.ACCENTS:
            arg = self.parse_arg()
            return Node("accent", name=name, arg=arg)

        if name in S.FRAC_CMDS:
            num = self.parse_arg()
            den = self.parse_arg()
            return Node("frac", num=num, den=den)

        if name == "sqrt":
            idx = None
            t = self.peek()
            if t is not None and t.type == "LBRACK":
                idx = self.parse_bracket_arg()
            arg = self.parse_arg()
            return Node("sqrt", arg=arg, index=idx)

        if name in S.TEXT_CMDS:
            raw = self.parse_text_arg()
            return Node("text", value=raw)

        if name == "ce":
            raw = self.parse_text_arg()
            return Node("chem", value=raw)

        if name in S.FUNCTIONS:
            return Node("func", name=name, power=None, sub=None, arg=None)

        if name == "left":
            return self.parse_left_right()

        if name == "begin":
            return self.parse_environment()

        if name == "|":
            return self.parse_norm()

        if name in ("{", "}"):
            return Node("punct", value=name)

        sym = S.lookup_symbol(name)
        if sym is not None:
            return Node("sym", name=name)

        # Unknown command: degrade gracefully by dropping it.
        return None

    # -- numbers ----------------------------------------------------------
    def parse_number(self):
        s = ""
        while True:
            t = self.peek()
            if t is not None and t.type == "CHAR" and t.value.isdigit():
                s += t.value
                self.advance()
            else:
                break
        # optional decimal part
        t = self.peek()
        if t is not None and t.type == "CHAR" and t.value == ".":
            save = self.pos
            self.advance()
            t2 = self.peek()
            if t2 is not None and t2.type == "CHAR" and t2.value.isdigit():
                s += "."
                while True:
                    t3 = self.peek()
                    if t3 is not None and t3.type == "CHAR" and t3.value.isdigit():
                        s += t3.value
                        self.advance()
                    else:
                        break
            else:
                self.pos = save
        return Node("num", value=s)

    # -- delimiters -------------------------------------------------------
    def parse_delim_chars(self, left, right):
        self.advance()  # opening
        right_type = {")": "RPAREN", "]": "RBRACK"}[right]
        inner = self.parse_sequence(stop_types=(right_type,))
        if self.peek() is not None and self.peek().type == right_type:
            self.advance()
        return Node("delim", left=left, right=right, body=inner)

    def parse_absval(self):
        self.advance()  # opening |
        inner = self._parse_until_char("|")
        return Node("delim", left="|", right="|", body=inner)

    def _parse_until_char(self, ch):
        items = []
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type == "CHAR" and t.value == ch:
                self.advance()
                break
            node = self.parse_scripted()
            if node is not None:
                items.append(node)
            else:
                # avoid infinite loop
                if self.peek() is t:
                    self.advance()
        return Seq(items)

    def parse_norm(self):
        inner_items = []
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type == "COMMAND" and t.value == "|":
                self.advance()
                break
            node = self.parse_scripted(stop_cmds=("|",))
            if node is not None:
                inner_items.append(node)
            else:
                if self.peek() is t:
                    self.advance()
        return Node("delim", left="||", right="||", body=Seq(inner_items))

    def parse_left_right(self):
        left = self._read_delim()
        inner = self.parse_sequence(stop_cmds=("right",))
        right = "."
        t = self.peek()
        if t is not None and t.type == "COMMAND" and t.value == "right":
            self.advance()
            right = self._read_delim()
        return Node("delim", left=left, right=right, body=inner)

    def _read_delim(self):
        t = self.peek()
        if t is None:
            return "."
        if t.type == "LPAREN":
            self.advance(); return "("
        if t.type == "RPAREN":
            self.advance(); return ")"
        if t.type == "LBRACK":
            self.advance(); return "["
        if t.type == "RBRACK":
            self.advance(); return "]"
        if t.type == "CHAR" and t.value in ("|", ".", "/"):
            self.advance(); return t.value
        if t.type == "COMMAND":
            self.advance()
            if t.value in ("{", "lbrace"):
                return "{"
            if t.value in ("}", "rbrace"):
                return "}"
            if t.value == "|":
                return "||"
            if t.value == "langle":
                return "<"
            if t.value == "rangle":
                return ">"
            return "."
        self.advance()
        return "."

    def parse_bracket_arg(self):
        self.advance()  # [
        inner = self.parse_sequence(stop_types=("RBRACK",))
        if self.peek() is not None and self.peek().type == "RBRACK":
            self.advance()
        return inner

    # -- text argument (raw) ----------------------------------------------
    def parse_text_arg(self):
        t = self.peek()
        if t is None or t.type != "LBRACE":
            # allow a single-token argument
            if t is not None:
                self.advance()
                return _clean_text(t.raw)
            return ""
        # position is at LBRACE; read raw until matching RBRACE
        i = self._idx()
        self.pos = i + 1  # consume LBRACE
        depth = 1
        raw = []
        while self.pos < len(self.toks) and depth > 0:
            tok = self.toks[self.pos]
            if tok.type == "LBRACE":
                depth += 1
                self.pos += 1
                continue
            if tok.type == "RBRACE":
                depth -= 1
                self.pos += 1
                if depth == 0:
                    break
                raw.append(tok.raw)
                continue
            raw.append(tok.raw)
            self.pos += 1
        return _clean_text("".join(raw))

    # -- big operators ----------------------------------------------------
    def parse_bigop(self, name):
        lower = upper = None
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type == "UNDERSCORE":
                self.advance()
                lower = self.parse_arg()
            elif t.type == "CARET":
                self.advance()
                upper = self.parse_arg()
            else:
                break
        return Node("bigop", name=name, lower=lower, upper=upper, body=None)

    # -- environments -----------------------------------------------------
    def parse_environment(self):
        name = self._read_braced_word()
        rows = []
        row = []
        while True:
            cell = self.parse_sequence(
                stop_types=("AMP", "DBACKSLASH"), stop_cmds=("end",)
            )
            row.append(cell)
            t = self.peek()
            if t is None:
                break
            if t.type == "AMP":
                self.advance()
                continue
            if t.type == "DBACKSLASH":
                self.advance()
                rows.append(row)
                row = []
                continue
            if t.type == "COMMAND" and t.value == "end":
                self.advance()
                self._read_braced_word()
                break
            break
        rows.append(row)
        return Node("env", name=name, rows=rows)

    def _read_braced_word(self):
        t = self.peek()
        if t is None or t.type != "LBRACE":
            return ""
        self.advance()
        chars = []
        while True:
            t = self.peek()
            if t is None or t.type == "RBRACE":
                if t is not None:
                    self.advance()
                break
            if t.type == "CHAR":
                chars.append(t.value)
            self.advance()
        return "".join(chars)


def _clean_text(raw):
    """Strip LaTeX command markup from a text-mode argument."""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == "\\":
            j = i + 1
            while j < n and (("a" <= raw[j] <= "z") or ("A" <= raw[j] <= "Z")):
                j += 1
            if j == i + 1:
                # escaped single char like \& -> &
                if j < n:
                    out.append(raw[j])
                    i = j + 1
                    continue
                i = j
                continue
            i = j
            out.append(" ")
            continue
        if c in "{}":
            i += 1
            continue
        out.append(c)
        i += 1
    return " ".join("".join(out).split())


def parse(source):
    """Parse a LaTeX source string into an expression tree (Seq node)."""
    return Parser(tokenize(source)).parse()
