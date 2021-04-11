from parser import Parser
from functor import Functor
from operators import *

@Functor
class Hello:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
    
    def __repr__(self):
        return f"HelloObject[['{self.s1}','{self.s2}']]"

class Binop:
    def __init__(self, op, a=None, b=None):
        self.op = op
        self.a = a
        self.b = b

    def __call__(self, a, b):
        self.a = a
        self.b = b
        return self

    def __repr__(self):
        return f"Binop[[{self.a} {self.op} {self.b}]]"

def JOIN(*iter):
    return "".join(iter)


# ps = String("HI")
ps = Hello [[ String("Hello") + ~Whitespaces + String("World") ]]
# print(ps.run("Hello World"))


# p2 = Terminal("Hello") / Terminal("Hi") + Terminal("World")
# print(p2.run("Hello World"))

Test = Binop % Times(Digit, 3)
mulOp = Binop % (Char("*") | Char("+"))
Addend = Binop % (Integer + Char("+") + Integer)
# print(Addend.run("5+4"))
KKK = ChainL1(mulOp, Integer)
print(KKK.run("5*2+3*4"))