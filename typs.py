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
        return str(x.value)
    elif isinstance(x, Token):
        return str(x.value)

    assert False
