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
        return f'Unconsumed="{self.rest}", Value={self.val}'

class NotParsed(Exception):
    pass

class Parser:

    # ONLY for use as a decorator
    def __init__(self, func):
        fname = getattr(func, "__name__", getattr(func, "__class__").__name__)
        self.__name__ = fname
        self.func = func

    @staticmethod
    def _stringParser(strVal):
        '''
        Construct a string parser for the given string. This is defined inside
        the class so that it can be used internally for other utilities.
        '''
        @Parser
        def run(inp):
            if inp.startswith(strVal):
                return ParserResult(inp[len(strVal):], (strVal,))
        return run

    def parse(self, inp):
        """
        Parse the given input and return either the result, or None if parsing 
        failed.
        """
        try:
            return self.run(inp).get()
        except NotParsed:
            return None

    def run(self, inp):
        """
        Internal function to run the parser and return updated state / output.
        """
        ret = self.func(inp)
        if ret is None:
            raise NotParsed()
        return ret
    
    def applicative(self, other):
        """
        Internal utility to implement `+` operator.
        """
        @Parser
        def run(inp):
            a = self.run(inp)
            b = other.run(a.rest)
            return ParserResult(b.rest, a.val + b.val)
        return run

    def alternative(self, other):
        """
        Internal utility to implement `|` operator.
        """
        @Parser
        def run(inp):
            try:
                return self.run(inp)
            except NotParsed:
                pass
            return other.run(inp)
        return run

    def map(self, callback):
        """
        Example:
        
            upperHello = String("Hello").map(lambda s: s.upper())

        Change the value of a parser based on some function. This is used to
        implement the Functor operators. The above example would store "HELLO"
        as the ouput value.
        """
        @Parser
        def run(inp):
            a = self.run(inp)
            return ParserResult(a.rest, callback(a.val))
        return run

    def to(self, val):
        """
        Example:
        
            helloParser = String("Hello").to("Hi")
        
        This will match and consume the string "Hello", but will store "Hi"
        as the value. Useful to create different objects based on strings.
        """
        return self.map(lambda _: val)

    ##################### Operator Overloads ###################################


    #############  Applicative: Do 1st, then 2nd, combine results
    
    def __add__(self, other):
        """
        Example:
        
            helloParser = String("Hello") + String("World")
        
        This will match the string "Hello", and then match "World". It will
        fail if any of these parsers fail.
        """
        if isinstance(other, str):
            other = self._stringParser(other)
        return self.applicative(other)
    
    def __radd__(self, other):
        """
        Example:
        
            helloParser = String("Hello") + String("World")
        
        This will match the string "Hello", and then match "World". It will
        fail if any of these parsers fail.
        """
        if isinstance(other, str):
            other = self._stringParser(other)
        return other.applicative(self)
        

    #############  Alternative: Try 1st, if fails try second.

    def __or__(self, other):
        """
        Example:
        
            helloParser = String("Hello") | String("Hi")
        
        This will match the string "Hello", and if not possible then it will
        try to match the string "Hi"
        """
        if isinstance(other, str):
            other = self._stringParser(other)
        return self.alternative(other)
    __truediv__ = __or__


    def __ror__(self, other):
        """
        Example:
        
            helloParser = String("Hello") | String("Hi")
        
        This will match the string "Hello", and if not possible then it will
        try to match the string "Hi"
        """
        if isinstance(other, str):
            other = self._stringParser(other)
        return other.alternative(self)
    __rtruediv__ = __ror__
    

    #############  Suppress result: Don't save the result of this parser.

    def __invert__(self):
        """
        Example:

            discardWhitespaces = ~Whitespaces
        
        This will consume the characters needed by PSR if successful, but will
        not store these values and will be discarded
        """
        return self.map(lambda _: ())
    

    ############# Functor: Apply a function onto the result of the parser
    #####################  Use % to unpack all values in function params

    def __mod__(self, container):
        """
        Example:

            mysum = lambda a, b: a + b
            sumParser = mysum % (Integer + ~Terminal("+") + Integer)
        
        This will consume run the parser, and then unpack the tuple of results
        from the parser into the arguments of the function. The result of the
        function evaluation will then be stored as the value
        """
        return self.map(lambda vals: container(*vals))
    __rmod__ = __mod__

    #####################  Use @ to pass in all values in a tuple to function

    def __matmul__(self, container):
        """
        Example:

            sumParser = sum @ SepBy(Integer, ~Terminal("+"))

                * the `sum()` function takes in an iterable
        
        This will consume run the parser, and then pass the tuple of values
        as an argument to the function. The result of the function evaluation 
        will then be stored as the value.

        Note that this is different from `%` as the values are passed as in 
        iterable, allowing you to use many of the inbuilt functions.
        """
        return self.map(lambda vals: container(vals))
    __rmatmul__ = __matmul__