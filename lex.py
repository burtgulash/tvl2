#!/usr/bin/env python3

import sys

from typs import Token, pp


abc = "abcdefghijklmnopqrstuvwxyz"
num = "0123456789"
punc = ".:;,-|~!@#$%^&*/+=?`<>'"

def lex(chars):
    status = None
    buf = ""
    for c in chars + "\0":
        #print ("  ", status, buf)

        if status is None:
            pass
        elif status == "underscore":
            if c == "_":
                buf += c
                continue
            if c in num:
                buf += c
                status = "num"
                continue
            if c.lower() in abc:
                buf += c
                status = "var"
                continue
            yield Token("num", buf)
            status, buf = None, ""
        elif status == "string":
            if c == "\\":
                buf += c
                status = "string_escape"
            elif c == '"':
                buf += c
                yield Token(status, buf)
                status, buf = None, ""
            continue
        elif status == "string_escape":
            if c in ('nr"\\'):
                buf += c
                status = "string"
                continue
            raise Exception(f"can't escape this character in string: {c}")
        elif status == "escape":
            if c.lower() in abc:
                buf += c
                status = "symbol"
                continue
            elif c in punc:
                buf += c
                status = "punc"
                continue
            elif c in "([{":
                buf += c
                yield Token("lparen", buf)
                status, buf = None, ""
                continue
            else:
                raise Exception(f"can't escape this character: {c}")
        elif status in ("symbol", "var"):
            if c.lower() in abc or c in num or c == "_":
                buf += c
                continue
            yield Token(status, buf)
            status, buf = None, ""
        elif status == "num":
            if c in num or c == "_":
                buf += c
                continue
            yield Token(status, buf)
            status, buf = None, ""
        elif status == "punc":
            if c in punc:
                buf += c
                continue
            yield Token(status, buf)
            status, buf = None, ""
        elif status in ("lparen", "rparen"):
            yield Token(status, buf)
            status, buf = None, ""

        if c in " \n\t":
            continue
        if c == "\0":
            yield Token("rparen", "EOF")

        buf += c
        if c == "\\":
            # TODO symbol_start. Symbol can only start with abc
            status = "escape"
        elif c == '"':
            status = "string"
        elif c.lower() in abc:
            status = "var"
        elif c == "_":
            status = "underscore"
        elif c in num:
            status = "num"
        elif c in punc:
            status = "punc"
        elif c in "([{":
            status = "lparen"
        elif c in ")]}":
            status = "rparen"


if __name__ == "__main__":
    x = sys.argv[1]
    with open(x) as f:
        x = f.read()
    print("LEX", x)
    x = list(lex(x))
    print(pp(x))
