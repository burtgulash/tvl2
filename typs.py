class Token:

    def __init__(self, T, value):
        self.T = T
        self.value = value

    def __repr__(self):
        return f"({self.value}::{self.T})"

    def __str__(self):
        return str(self.value)


class Value:

    def __init__(self, T, value):
        self.T = T
        self.value = value

    def __repr__(self):
        if self.T == "builtin":
            return f"{self.T}"
        if self.T == "special":
            return f"{self.T}"
        return f"({self.value}::{self.T})"

    def __str__(self):
        return str(self.value)

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
        return x.value
    elif isinstance(x, Token):
        return x.value
    assert False
