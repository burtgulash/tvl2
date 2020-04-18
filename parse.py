#!/usr/bin/env python3

import sys

import lex
from typs import Box, Token, NIL, pp


end_paren = {
    "(": ")",
    "[": "]",
    "{": "}",
    "\(": ")",
    "\[": "]",
    "\{": "}",
}

def flush_til(buf, outq, lvl):
    R = buf.pop()
    while outq:
        if outq[-1][1] > lvl:
            break
        H = outq.pop()[0]
        L = buf.pop()
        R = [L, H, R]
    return R

def box(lparen, x):
    if lparen == "(":
        return x
    if lparen == "{":
        return Box("lambda", x)
    if lparen == "[":
        return Box("box", x)
    if lparen == r"\(":
        return Box("block", x)
    if lparen == r"\{":
        return Box("quote", x)
    if lparen == r"\[":
        return Box("unquote", x)
    assert False


def pparse(toks):
    tok = next(toks)
    if tok.T == "rparen":
        x, end = tok, True
    elif tok.T == "lparen":
        end = None
        x = parse(end_paren[tok.value], toks)
        x = box(tok.value, x)
    else:
        x, end = tok, None
    return x, end

def parse(expected_end, toks):
    buf, outq = [], []

    L, end = pparse(toks)
    if end and L.value == expected_end:
        return NIL

    buf.append(L)

    while True:
        H, end = pparse(toks)
        if end and H.value == expected_end:
            break

        R, end = pparse(toks)
        if end:
            raise Exception("can't END on R")

        lvl = 0
        right = 0
        if isinstance(H, Token):
            op = H.value

            if op.startswith(":"):
                right = 1

            if op == "->":
                lvl = 7
            elif op == "|":
                lvl = 6
                right = 1
            elif op in (":|", "||"):
                lvl = 5
                right = 1
            elif op == ("?"):
                lvl = 4
            elif op in (":=", "::=", "?="):
                lvl = 4
                right = 1
            elif op == ";":
                lvl = 3
                right = 1
            elif op == ",":
                lvl = 2
            elif op in ("+", "-"):
                lvl = 0
            elif op in ("*", "/"):
                lvl = -1
            elif op == "$":
                lvl = -2
            elif op == "::":
                lvl = -3
            elif op in (".", ":"):
                lvl = -4

        assert right in (0, 1)
        buf.append(flush_til(buf, outq, lvl - right))
        buf.append(R)
        outq.append((H, lvl))

    return flush_til(buf, outq, 999)


def Parse(x):
    x = lex.lex(x)
    x = parse("EOF", x)
    return x


if __name__ == "__main__":
    x = sys.argv[1]
    print(x)
    x = lex.lex(x)
    x = parse("EOF", x)
    x = pp(x)
    print(x)
