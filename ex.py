#!/usr/bin/env python3

import sys

import lex
import parse
from typs import Box, Fn, Token, Value, NIL, ZERO, ONE, pp


def cons_size_(x, typ):
    if isinstance(x, Value) and x.T == "cons" and x.value[2] == typ:
        return cons_size_(x.value[0], typ) + cons_size_(x.value[1], typ)
    return 1

def cons_typ_(x):
    if isinstance(x, Value) and x.T == "cons":
        return x.value[2]
    return None

def print_(x, y, _):
    print(x.value)
    return x

def NUM(x):
    return Value("num", x)

def from_bool_(x):
    return [ZERO, ONE][x]

def cons(x, y, typ):
    return Value("cons", [x, y, typ])

def ask_(x, y, _):
    assert x.T == "num"
    if x.value == 0:
        return NIL
    return y

def else_(x, y, _):
    if x is NIL:
        return y
    return x

def continue_(x, y, _):
    return y


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


def fn_(head, body, env):
    x_var = y_var = None

    if isinstance(head, Value) and head.T == "cons":
        x_var = head.value[0]
        assert isinstance(x_var, Value) and x_var.T == "sym"
        x_var = x_var.value[1:]

        y_var = head.value[1]
        assert isinstance(y_var, Value) and y_var.T == "sym"
        y_var = y_var.value[1:]
    elif isinstance(head, Value) and head.T == "sym":
        assert isinstance(head, Value) and head.T == "sym"
        x_var = head.value[1:]
    elif head is NIL:
        pass
    else:
        assert False

    assert isinstance(body, Box) and body.T == "block"
    return Value("fn", Fn(env, x_var, y_var, body.value))


def assign_(x, y, env):
    if isinstance(x, Value) and x.T == "cons":
        if y.T != "cons": assert False

        x_dirn, y_dirn = x.value[2], y.value[2]
        if x_dirn != y_dirn: assert False

        xl, xr = x.value[0], x.value[1]
        yl, yr = y.value[0], y.value[1]

        assign_(xl, yl, env)
        assign_(xr, yr, env)
    elif isinstance(x, Box) and x.T == "box":
        if not (isinstance(y, Box) and y.T == "box"): assert False
        assign_(x.value, y.value, env)
    elif isinstance(x, Value):
        if x.T == "sym":
            env[1][x.value[1:]] = y
        else: assert False
    else: assert False
    return y

def match__(x, y, env):
    if isinstance(x, Value) and x.T == "cons":
        if y.T != "cons": return False

        x_dirn, y_dirn = x.value[2], y.value[2]
        if x_dirn != y_dirn: return False

        xl, xr = x.value[0], x.value[1]
        yl, yr = y.value[0], y.value[1]

        if not match__(xl, yl, env): return False
        if not match__(xr, yr, env): return False
    elif isinstance(x, Box) and x.T == "box":
        if not (isinstance(y, Box) and y.T == "box"): return False

        m = match__(x.value, y.value, env)
        if not m: return m
    elif isinstance(x, Value):
        if x.T == "sym":
            env[1][x.value[1:]] = y
        else: return False
    else: return False
    return True

def match_(x, y, env):
    if match__(x, y, env):
        return ONE
    return NIL


def ex(env, x):
    in_func = False
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
                if x.value == "_":
                    x = NIL # TODO infinity bo co?
                    continue
                x = x.value
                negative = x.startswith("_")
                x = x.replace("_", "")
                x = int(x)
                if negative:
                    x = -x
                x = Value("num", x)
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
                if in_func:
                    env = env[0]
                env = (env, {"x": L, "y": R})
                x = H.value
                #x = ex(env1, H.value)
            elif isinstance(H, Value) and H.T == "fn":
                if in_func:
                    env = env[0]

                fn = H.value
                env_ = {}
                if fn.x_var is not None:
                    env_[fn.x_var] = L
                if fn.y_var is not None:
                    env_[fn.y_var] = R
                env = (fn.env, env_)

                x = fn.body
                #x = ex(env1, fn.body)
            else:
                raise Exception(f"Can't process non function: {type(H).__name__}::{H.T}")
        else:
            raise AssertionError(f"eval: Can't evaluate {x}")

    # clean up func env
    if in_func:
        env = env[0]

    return x


ENV = (None, {
    # cons
    ".": Value("builtin", lambda x, y, _: cons(x, y, ".")),
    ":": Value("builtin", lambda x, y, _: cons(x, y, ":")),
    ",": Value("builtin", lambda x, y, _: cons(x, y, ",")),
    ";": Value("builtin", lambda x, y, _: cons(x, y, ";")),
    "Size": Value("builtin", lambda x, y, _: NUM(cons_size_(x, cons_typ_(x)))),

    # arithmetic
    "+": Value("builtin", lambda x, y, _: NUM(x.value + y.value)),
    "-": Value("builtin", lambda x, y, _: NUM(x.value - y.value)),
    "*": Value("builtin", lambda x, y, _: NUM(x.value * y.value)),
    "==": Value("builtin", lambda x, y, _: from_bool_(x.value == y.value)),

    # control flow
    "?": Value("special", ask_),
    ":|": Value("special", else_),
    "|": Value("special", continue_),

    # misc
    "$": Value("builtin", lambda x, y, env: env_lookup(env, y.value[1:])),
    "->": Value("builtin", fn_),
    "qq": Value("builtin", qq_),
    ":-": Value("builtin", assign_), # TODO
    ":=": Value("builtin", lambda x, y, env: match_(x, y, env)), # TODO
    "::=": Value("builtin", lambda x, y, env: match_(x, y, env[0])), # TODO
    "-:": Value("builtin", lambda x, y, env: assign_(y, x, env)), # TODO
    "=:": Value("builtin", lambda x, y, env: match_(y, x, env)), # TODO
    "ENV": Value("builtin", lambda x, y, env: Value("env", env[1])),

    # help
    "pr": Value("builtin", print_),
})

# test fns
#ENV[1]["foo"] = Value("fn", Fn(ENV, "a", "b", parse.Parse("a+b+b")))


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
    print("  PARSED:", pp(x))

    x = ex(ENV, x)
    print(pp(x))
