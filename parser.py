from parserResult import ParserResult

class Parser:
    # ONLY for use as a decorator
    def __init__(self, func):
        self.func = func

    def run(self, inp):
        return self.func(inp)
    
    def __add__(self, other):
        @Parser
        def applicative(inp):
            a = self.run(inp)
            if not a:
                return ParserResult(inp)
            b = other.run(a.rest)
            if not b:
                return ParserResult(inp)
            return ParserResult(b.rest, a.ans + b.ans)
        return applicative

    def __or__(self, other):
        @Parser
        def alternative(inp):
            a = self.run(inp)
            if a:
                return a
            b = other.run(inp)
            if b:
                return b
            return ParserResult(inp)
        return alternative
    
    __truediv__ = __or__

    def __invert__(self):
        @Parser
        def ignored(inp):
            a = self.run(inp)
            if a:
                return ParserResult(a.rest, ())
            return ParserResult(inp)
        return ignored
    
    def concat(self):
        @Parser
        def concat(inp):
            a = self.run(inp)
            if a:
                return ParserResult(a.rest, ("".join(a.ans),))
            return ParserResult(inp)
        return concat

    def __rmod__(self, container):
        @Parser
        def functor(inp):
            a = self.run(inp)
            if a:
                return ParserResult(a.rest, (container(*a.ans),))
            return ParserResult(inp)
        return functor
    
    __mod__ = __rmod__