#!/usr/bin/env python3

import sys

import lex
from parse import parse, pp
from typs import Token, Value, NIL, ELSE


def cons_(x, y, _):
    return Value("cons", [x, y])

def plus_(x, y, _):
    assert x.T == y.T == "num"
    return Value("num", x.value + y.value)

def ask_(x, y, _):
    assert x.T == "num"
    if x.value == 0:
        return ELSE
    print("1")
    return y

def else_(x, y, _):
    if x is ELSE:
        return y
    return x


def ex(env, x):
    while True:
        if isinstance(x, Value):
            if x.T == "var":
                x = env_lookup(env, x.value)
                continue
            if x.T == "box":
                x = ex(env, x.value)
                x = Value("box", x)
            break
        elif isinstance(x, Token):
            if x.T == "num":
                x = Value("num", int(x.value))
            elif x.T == "symbol":
                x = Value("sym", x.value[1:])
            elif x.T == "string":
                x = Value("str", x.value)
            elif x.T in ("punc", "var"):
                x = Value("var", x.value)
                continue
            else:
                raise Exception("Can't parse this")
            break
        elif isinstance(x, list):
            L = ex(env, x[0])
            H = ex(env, x[1])

            R = x[2]
            if H.T != "special":
                R = ex(env, R)

            assert H.T in ("builtin", "special")
            x = H.value(L, R, env)
        else:
            raise AssertionError("eval: Can only process list or TUPLE")

    return x


FNS = {
    ".": Value("builtin", cons_),
    "+": Value("builtin", plus_),
    "?": Value("special", ask_),
    ":|": Value("special", else_),
}

def env_lookup(env, key):
    while True:
        parent, env_dict = env
        if key in env_dict:
            return env_dict[key]
        if not parent:
            raise Exception(f"Can't env lookup: {key}")
        env = parent


if __name__ == "__main__":
    x = sys.argv[1]
    print("LEX", x)
    x = parse("EOF", lex.lex(x))
    print("PAR", pp(x))

    env = (None, {
        **FNS,
    })
    x = ex(env, x)
    print(pp(x))
