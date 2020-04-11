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
ELSE = Value("else", "else")


def pp(x):
    if isinstance(x, list):
        return "({})".format(" ".join(map(pp, x)))
    elif isinstance(x, Box):
        if x.T == "block":
            return "\({})".format(pp(x.value))
        if x.T == "box":
            return "[{}]".format(pp(x.value))
        if x.T == "quote":
            return "{{{}}}".format(pp(x.value))
    elif isinstance(x, Value):
        if x.T == "cons":
            return "({}.{})".format(pp(x.value[0]), pp(x.value[1]))
        if x.T == "fn":
            fn = x.value
            return "Fn({}.{} -> ...)".format(fn.x_var, fn.y_var)
        return str(x.value)
    elif isinstance(x, Token):
        #return "T:" + str(x.value)
        return str(x.value)

    assert False
