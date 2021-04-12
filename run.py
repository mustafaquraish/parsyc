from parser import Parser
from operators import *

from util import curried


@curried
class Binop:
    def __init__(self, op, a, b):
        self.op = op
        self.a = a
        self.b = b

    def __repr__(self):
        return f"({self.a} {self.op} {self.b})"

    def eval(self):
        a = self.a if isinstance(self.a, int) else self.a.eval()
        b = self.b if isinstance(self.b, int) else self.b.eval()
        return a+b if self.op=="+" else \
               a-b if self.op=="-" else \
               a/b if self.op=="/" else \
               a*b if self.op=="*" else \
               a%b if self.op=="%" else \
               a^b if self.op=="^" else \
               None

def facorial(n):
    from functools import reduce
    return reduce(lambda a,b: a*b, range(1,n+1), 1)

@curried
class Unop:
    def __init__(self, op, a):
        self.op = op
        self.a = a

    def __repr__(self):
        if self.op != "!":
            return f"({self.op}{self.a})"
        else:
            return f"({self.a}{self.op})"

    def eval(self):
        a = self.a if isinstance(self.a, int) else self.a.eval()
        return -a if self.op=="-" else \
               ~a if self.op=="~" else \
                facorial(a) if self.op=="!" else \
                None

ops_precedence = [
    ("unary", Unop % Terminal("!"), "post"),
    ("unary", Unop % (Terminal("-") | Terminal("~")), "pre"),
    ("binary", Binop % Terminal("/"), "left"),
    ("binary", Binop % Terminal("*"), "left"),
    ("binary", Binop % Terminal("+"), "left"),
    ("binary", Binop % Terminal("-"), "right"),
    ("binary", Binop % Terminal("%"), "right"),
    ("binary", Binop % Terminal("^"), "right"),
]

integer = int % (Some(Digit) + ~Whitespaces)
atom = forward(lambda: integer | Between("(", ")", equation) )
equation = BuildExpressionParser(atom, ops_precedence)

res = equation.parse("5 + -4 / 3 / 2 * 2 - 1")
print(res)          # --> ((5 + (((4 / 3) / 2) * 2)) - 1)
print(res.eval())   # --> 5.333

res = equation.parse("5!")
print(res)          # --> ((5 + (((4 / 3) / 2) * 2)) - 1)
print(res.eval())   # --> 5.333

res = equation.parse("5 + -4 / ~3 / 2 * 2 - 1")
print(res)          # --> ((5 + (((4 / 3) / 2) * 2)) - 1)
print(res.eval())   # --> 5.333

