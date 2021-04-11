from parserResult import ParserResult
from parser import Parser

def Functor(fcn):
    class wrapped(Parser):
        def __init__(self, fcn, psr=None):
            self.fcn = fcn
            self.psr = psr
        
        def run(self, inp):
            res = self.psr.run(inp)
            if not res:
                return ParserResult(inp)
            return ParserResult(res.rest, (self.fcn(*res.ans),))

        def __matmul__(self, psr):
            """
            Allows you to wrap a Parser with @ notation. For instance:

            Join @ Many(String("+") | Sting("-"))
            Join @ (String("A") + String("B") | String("C"))
            """
            self.psr = psr
            return self

        def __getitem__(self, psr):
            """
            Allows you to wrap a Parser with [[ ]] notation. For instance:

            Join [[ Many(String("+") | Sting("-")) ]]

            Note that this function is set up to work with nested arrays so you
            must use [[ ]] instead of just [ ]
            """
            self.psr = psr[0]
            return self

        def __mul__(self, fnctr):
            """
            Allows you to compose functors using `*`. For instance:

            Integer = (ToInt * Join) @ Many(Digit)
            """
            return wrapped(fnctr.fcn, self)

    return wrapped(fcn)

