from parser import Parser
from operators import *

from util import curried

class Hello:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
    
    def __repr__(self):
        return f"HelloObject[['{self.s1}','{self.s2}']]"

@curried
class Binop:
    def __init__(self, op, a, b):
        self.op = op
        self.a = a
        self.b = b

    def __repr__(self):
        return f"Binop[[{self.a} {self.op} {self.b}]]"


@curried
class Movement:
    def __init__(self, direction, distance):
        self.dir = direction
        self.dist = distance
    def __repr__(self):
        return f'{self.dir} -> {self.dist} steps'

# # ps = String("HI")
# ps = Hello [[ String("Hello") + ~Whitespaces + String("World") ]]
# print(ps.run("Hello World"))


# p2 = Terminal("Hello") / Terminal("Hi") + Terminal("World")
# print(p2.run("Hello World"))

Test = Binop % Times(Digit, 3)
mulOp = Binop % (Char("*") | Char("+"))
Addend = Binop % (Integer + Char("+") + Integer)
# print(Addend.run("5+4"))

AAA = ChainL1(mulOp, Integer)
BBB = ChainR1(mulOp, Integer)
print(AAA.run("5*2+3*4"))
print(BBB.run("5*2+3*4"))

qq = mulOp
# print(qq.run("*4"))

p = String("Hi") | String("Hello")
# print(p.run("Hello"))


dirParser = Movement % (Terminal("Forward").to("F") / Terminal("Backward").to("B") + ~Whitespaces + Integer)
print(dirParser.run("Forward 10"))