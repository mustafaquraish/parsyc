from .parser import Parser, ParserResult, NotParsed

########################### Functors to wrap data ##############################

Join = "".join
Tuple = lambda iter: (iter,)
Tuplify = lambda func: lambda *iter: func(iter)

########################### Basic parsers ######################################


def Times(psr, mn, mx=-1):
    if (mx and mx < 0): 
        mx = mn
    @Parser
    def run(inp):
        count = 0
        res = ParserResult(inp, ()) 
        while True:
            try:
                temp = psr.run(res.rest)
            except NotParsed:
                if count >= mn:
                    return res
                break
            count += 1
            if (mx and count > mx):
                return res
            res = ParserResult(temp.rest, res.val + temp.val)
    return run

def Many(psr):      return Times(psr, 0, None)
def Many1(psr):     return Times(psr, 1, None)
def Some(psr):      return Times(psr, 1, None)
def Optional(psr):  return Times(psr, 0, 1)


@Parser
def AnyChar(inp):
    if len(inp)>0: 
        return ParserResult(inp[1:], inp[0])

def Char(char):
    @Parser
    def run(inp):
        if len(inp)>0 and inp[0]==char: 
            return ParserResult(inp[1:], inp[0])
    return run

def CharSatisfy(condition):
    @Parser
    def run(inp):
        if len(inp)>0 and condition(inp[0]):
            return ParserResult(inp[1:],inp[0])
    return run

@Parser
def EOF(inp):
    if len(inp)==0:
        return ParserResult(inp,())

def String(strVal): return Parser._stringParser(strVal)

def StringOneOf(*strs):
    p = String(strs[0])
    for s in strs[1:]:
        p = p | String(s)
    return p

Whitespace = String(" ") | String("\n") | String("\t")
Whitespaces = Join @ Many(Whitespace)

Digit = CharSatisfy(str.isdigit)
Integer = int % ( Join @ (Optional(String("-") | String("+")) 
                          + Some(Digit)
                          + ~Whitespaces) )

Float = (Optional(Char("+") | Char("-")) +
            (
                ( Optional(Some(Digit)) + Char(".") + Some(Digit) ) |
                ( Some(Digit) + Optional(Char(".") + Many(Digit)) )
            ) +
            Optional(Char("e") + Some(Digit)) +
            ~Whitespaces
        ) @ Join % float

def Terminal(strVal): return String(strVal) + ~Whitespaces
    
def Identifier(keywords):
    @Parser
    def run(inp):
        idparser = Join @ ( CharSatisfy(str.isalpha) / Char("_") + 
                            Many(CharSatisfy(str.isalnum) | Char("_")) 
                          )
                        
        res = idparser.run(inp)
        if res.val[0] not in keywords:
            return res
    return run + ~Whitespaces

def SepBy(psr, sep):
    return psr + Many(sep + psr) + ~Whitespaces

def ManyUntil(psr, end):
    @Parser
    def run(inp):
        res = ParserResult(inp, ())
        while True:
            try:
                temp = end.run(res.rest)
                return ParserResult(temp.rest, res.val + temp.val)
            except NotParsed:
                pass
            temp = psr.run(res.rest)
            res = ParserResult(temp.rest, res.val + temp.val)

    return run

def Regex(rgx,group=0):
    import re
    compiled = re.compile(rgx)
    if not isinstance(group, tuple):
        group = (group,)
    @Parser
    def run(inp):
        res = compiled.match(inp)
        if res: 
            return ParserResult(inp[res.end():], res.group(*group))
    return run

def Between(begin, end, psr, ignoreEnds=True):
    if ignoreEnds: 
        return ~Terminal(begin) + psr + ~Whitespaces + ~Terminal(end)
    else:
        return Terminal(begin) + psr + ~Whitespaces + Terminal(end)


def forward(fn):
    """
    Used to forward declare a parser so that it can use parsers that are 
    defined later in the file. This is helpful for mutually recursive parsers!
    Example usage:

        atom = forward(lambda: Integer | Between("(", ")", equation)))
        equation = atom + Terminal("*") + atom

    """
    @Parser
    def run(inp):
        return fn().run(inp)
    return run

def ChainL1(operator, operand):
    @Parser
    def run(inp):
        res = operand.run(inp)        
        def more(res):
            try:
                op = operator.run(res.rest)
                b = operand.run(op.rest)
                newRes = ParserResult(b.rest, op.get()(*res.val, *b.val))
                return more(newRes)
            except NotParsed:
                return res

        return more(res)
    return run


def ChainR1(operator, operand):
    @Parser
    def run(inp):
        res = operand.run(inp)
        def func(f, y):
            return f(*(res.val), y)
        try:
            return (func % (operator + ChainR1(operator,operand))).run(res.rest)
        except NotParsed:
            return res
    return run

def ChainUnaryPre(operator, operand):
    @Parser
    def run(inp):
        try:
            a = operator.run(inp)
            b = ChainUnaryPre(operator, operand).run(a.rest)
            return ParserResult(b.rest, a.get()(*b.val))
        except NotParsed:
            pass
        return operand.run(inp)
    return run

def ChainUnaryPost(operator, operand):
    @Parser
    def run(inp):
        a = operand.run(inp)
        while True:
            try:
                b = operator.run(a.rest)
                a = ParserResult(b.rest, b.get()(*a.val))
            except NotParsed:
                return a
    return run

def BuildExpressionParser(base, opsTable):
    """
    Build an expression from the given operations table corresponding to the
    precedence of the operators. `base` has the highest precedence (usually
    a literal value or a parenthesized expression). The opsTable is used to 
    heirarchically build parsers that respect the order of precedence.
    
    Each item in the table should be a 3-tuple
    with the following elements:

        [
            (type, parser, assoc)
        ]
    
    Where:
    - `type` is in ["unary", "binary"] corresponding to unary/binary expressions
    - `parser` is a Parser that returns a unary/binary function which is applied
               to the parsed operands
    - `assoc` depends on `type`.
        - For unary, it is in ["pre", "post"], to specify prefix/postfix ops
        - For binary, it is in ["left", "right"] to specify associativity

    """

    curLevel = base
    mapping = {
        ("unary", "pre"):    ChainUnaryPre,
        ("unary", "post"):   ChainUnaryPost,
        ("binary", "left"):  ChainL1,
        ("binary", "right"): ChainR1,
    }
    for typ, op, assoc in opsTable:
        if (typ, assoc) in mapping:
            curLevel = mapping[(typ, assoc)](op, curLevel)
        else:
           raise Exception(f"\n\n{(typ, '_', assoc)} is invalid.\n"
                            " - Valid options are:\n"
                            '       ("unary" , _ , "pre"  )\n'
                            '       ("unary" , _ , "post" )\n'
                            '       ("binary", _ , "left" )\n'
                            '       ("binary", _ , "right")\n')
    return curLevel