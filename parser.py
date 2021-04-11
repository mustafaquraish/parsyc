class ParserResult:   
    def __init__(self, rest, val=None):
        self.rest = rest
        if type(val) != tuple:
            val = (val,)
        self.val = val

    def get(self):
        if len(self.val) == 1:
            return self.val[0]
        else:
            return self.val

    def __repr__(self):
        return f'Uncomsumed="{self.rest}", Value={self.val}'

class NotParsed(Exception):
    pass

class Parser:

    # ONLY for use as a decorator
    def __init__(self, func):
        self.func = func

    def parse(self, inp):
        try:
            return self.run(inp).get()
        except NotParsed:
            return None

    def run(self, inp):
        ret = self.func(inp)
        if ret is None:
            raise NotParsed()
        return ret
    
    def __add__(self, other):
        @Parser
        def applicative(inp):
            a = self.run(inp)
            b = other.run(a.rest)
            return ParserResult(b.rest, a.val + b.val)
        return applicative

    def modify(self, callback):
        @Parser
        def run(inp):
            a = self.run(inp)
            return ParserResult(a.rest, callback(a.val))
        return run

    def to(self, val):
        return self.modify(lambda _: val)

    def __or__(self, other):
        @Parser
        def alternative(inp):
            try:
                return self.run(inp)
            except NotParsed:
                pass
            return other.run(inp)
        return alternative
    
    __truediv__ = __or__

    def __invert__(self):
        return self.modify(lambda _: ())
    
    def __rmod__(self, container):
        return self.modify(lambda vals: container(*vals))

    def __lshift__(self, other):
        return self + ~other

    def __rshift__(self, other):
        return ~self + other

    __mod__ = __rmod__