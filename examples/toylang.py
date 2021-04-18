from dataclasses import dataclass
from parsyc import *

KEYWORDS = ["print"]

class Expression: pass
class Statement: pass
class Value(Expression): pass

@dataclass
class VarDefn(Statement):
    name: str ; body: Expression
    def eval(self, scope): scope[self.name] = self.body.eval(scope)

@dataclass
class PrintStmt(Statement):
    body: Expression
    def eval(self, scope): print(self.body.eval(scope))

@curried
@dataclass
class Binop(Expression):
    op: str ; a: Expression ; b: Expression
    def eval(self, scope):
        a, b = self.a.eval(scope), self.b.eval(scope)
        return a+b if self.op=="+" else     a-b if self.op=="-" else \
               a/b if self.op=="/" else     a*b if self.op=="*" else \
               a%b if self.op=="%" else     a**b if self.op=="**" else \
               None

@dataclass
class Negate(Expression):
    a: Expression
    def eval(self, scope): return -self.a.eval(scope)

@dataclass
class Variable(Value):
    name: str
    def eval(self, scope): return scope[self.name]

@dataclass
class Literal(Value):
    val: float
    def eval(self, scope): return self.val

@dataclass
class Block:
    stmts: list[Statement]
    def eval(self, scope=None):
        if scope is None: scope = {}
        for s in self.stmts: s.eval(scope)

@dataclass
class ForLoop(Statement):
    var:str ; lmin: Value ; lmax: Value ; body: Block
    def eval(self, scope):
        lmin = int(self.lmin.eval(scope))
        lmax = int(self.lmax.eval(scope))
        for i in range(lmin, lmax+1): 
            scope[self.var] = i
            self.body.eval(scope)

################################################################################

ops_precedence = [("binary",    Binop % Terminal("**"), "left"),
                  ( "unary", Terminal("-").to(Negate), "pre"),
                  ("binary",    Binop % Terminal("/"), "left"),
                  ("binary",    Binop % Terminal("*"), "left"),
                  ("binary",    Binop % Terminal("+"), "left"),
                  ("binary",    Binop % Terminal("-"), "right"),
                  ("binary",    Binop % Terminal("%"), "right")]

valueP = (Literal % Float) | (Variable % Identifier(KEYWORDS))
atom = forward(lambda: valueP | BetweenStr("(", ")", exprP))
exprP = BuildExpressionParser(atom, ops_precedence)
blockP = forward(lambda: Block @ Many(statementP))
statementP = (VarDefn % (Identifier(KEYWORDS) + ~Terminal("=") + exprP) |
              PrintStmt % (~Terminal("print") + exprP) |
              ForLoop % (~Terminal("for") + Identifier(KEYWORDS) + 
                          ~Terminal("=") + valueP + ~Terminal(":") + valueP +
                          BetweenStr("{", "}", blockP)) | 
              ~(Terminal("#") + ManyUntil(AnyChar, Char("\n"))+ Whitespaces))
toylangP = ~Whitespaces + blockP + ~EOF

################################################################################

testCode = """
#### Leibniz Formula for PI 

# Number of iterations
n = 1000 

sum = 0
for i = 0 : n {
    sum = sum + (-1)**i/(2*i + 1)
}

print(sum*4)
"""

res = toylangP.parse(testCode)
if res is None:
    print("Parse Error! Invalid code")
else:
    # for stmt in res.stmts:
    #     print(stmt)
    res.eval()