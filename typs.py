class Token:

    def __init__(self, T, value):
        self.T = T
        self.value = value


class Value:

    def __init__(self, T, value):
        self.T = T
        self.value = value


class Box:

    def __init__(self, T, value):
        self.T = T
        self.value = value


class Fn:

    def __init__(self, env, x_var, y_var, body):
        self.env = env
        self.x_var = x_var
        self.y_var = y_var
        self.body = body


NIL = Value("nil", "()")
ZERO = Value("num", 0)
ONE = Value("num", 1)


def pp(x):
    if isinstance(x, list):
        return "({})".format(" ".join(map(pp, x)))
    elif isinstance(x, Box):
        if x.T == "block":
            return "\({})".format(pp(x.value))
        if x.T == "box":
            return "[{}]".format(pp(x.value))
        if x.T == "quote":
            return "[{}]".format(pp(x.value))
        if x.T == "unquote":
            return "\[{}]".format(pp(x.value))
    elif isinstance(x, Value):
        if x.T == "cons":
            sep = x.value[2]
            x, y = x.value[0], x.value[1]
            return "({}{}{})".format(pp(x), sep, pp(y))
        if x.T == "fn":
            fn = x.value
            return "Fn({}.{} -> ...)".format(fn.x_var, fn.y_var)
        if x.T == "builtin":
            return "BFn"
        if x.T == "env":
            d = {k: pp(v) for k, v in x.value.items()}
            return "Dict({})".format(d)
        return str(x.value)
    elif isinstance(x, Token):
        #return "T:" + str(x.value)
        return str(x.value)

    assert False
