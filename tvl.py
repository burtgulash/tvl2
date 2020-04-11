#!/usr/bin/env python3

import sys

import lex
import parse
from typs import Box, Fn, Token, Value, NIL, ELSE, pp


def cons_(x, y, _):
    return Value("cons", [x, y])

def plus_(x, y, _):
    assert x.T == y.T == "num"
    return Value("num", x.value + y.value)

def ask_(x, y, _):
    assert x.T == "num"
    if x.value == 0:
        return ELSE
    return y

def else_(x, y, _):
    if x is ELSE:
        return y
    return x


def qq_(x, _, env):
    if isinstance(x, (Token, Value)):
        pass
    elif isinstance(x, Box):
        if x.T == "quote":
            x = ex(env, x.value)
        else:
            x = Box(x.T, qq_(x.value, None, env))
    elif isinstance(x, list):
        x = [qq_(x_, None, env) for x_ in x]
    else:
        assert False

    return x


def fn_(x, _, env):
    x_var = y_var = None

    print("X", x.value[0].value)

    if isinstance(x, Value) and x.T == "cons":
        x = x.value[1]
        head = x.value[0]

        print("HEAD", head.value)
        print("BODY", type(x))
        if isinstance(head, Value) and head.T == "cons":
            print("TU")
            x_var = head.value[0]
            assert isinstance(x_var, Value) and x_var.T == "sym"
            x_var = x_var.value[1:]

            y_var = head.value[1]
            assert isinstance(y_var, Value) and y_var.T == "sym"
            y_var = y_var.value[1:]
        else:
            assert isinstance(head, Value) and head.T == "sym"
            x_var = head.value[1:]

    assert isinstance(x, Box) and x.T == "block"

    return Fn(env, x_var, y_var, body)



def ex(env, x):
    while True:
        if isinstance(x, Value):
            if x.T == "var":
                x = env_lookup(env, x.value)
                continue
            break
        elif isinstance(x, Box):
            if x.T == "block":
                break
            if x.T == "box":
                x = ex(env, x.value)
                x = Box("box", x)
                break
            if x.T == "quote":
                x = qq_(x.value, None, env)
                break
            assert False
        elif isinstance(x, Token):
            if x.T == "num":
                x = Value("num", int(x.value))
            elif x.T == "symbol":
                x = Value("sym", x.value)
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
            if not (isinstance(H, Value) and H.T == "special"):
                R = ex(env, R)

            if isinstance(H, Value) and H.T in ("builtin", "special"):
                x = H.value(L, R, env)
            elif isinstance(H, Box) and H.T == "block":
                env1 = {}
                env1["x"] = L
                env1["y"] = R
                env1 = (env, env1)

                x = ex(env1, H.value)
            elif isinstance(H, Value) and H.T == "fn":
                fn = H.value
                env1 = {}
                if fn.x_var is not None:
                    env1[fn.x_var] = L
                if fn.y_var is not None:
                    env1[fn.y_var] = R
                env1 = (fn.env, env1)

                x = ex(env1, fn.body)
            else:
                raise Exception(f"Can't process non function: {type(H).__name__}::{H.T}")
        else:
            raise AssertionError("eval: Can only process list or TUPLE")

    return x


CONS = Value("builtin", cons_)

ENV = (None, {
    # cons
    ".": CONS,
    ":": CONS,
    ",": CONS,
    ";": CONS,

    # arithmetic
    "+": Value("builtin", plus_),

    # conditionals
    "?": Value("special", ask_),
    ":|": Value("special", else_),

    # misc
    "qq": Value("builtin", qq_),
    "fn": Value("builtin", fn_),
})

# test fns
ENV[1]["foo"] = Value("fn", Fn(ENV, "a", "b", parse.Parse("a+b+b")))


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
    x = parse.Parse(x)
    print("PAR", pp(x))

    x = ex(ENV, x)
    print(pp(x))
