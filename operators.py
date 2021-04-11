from parser import Parser, ParserResult, NotParsed

########################### Functors to wrap data ##############################

Join = lambda *iter: "".join(iter)

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

def String(strVal):
    @Parser
    def run(inp):
        if inp.startswith(strVal):
            return ParserResult(inp[len(strVal):], (strVal,))
    return run

Whitespace = String(" ") | String("\n") | String("\t")
Whitespaces = Join % Many(Whitespace)

Digit = CharSatisfy(str.isdigit)
Integer = int % ( Join % (Optional(String("-") | String("+")) + Some(Digit)) )

def Terminal(strVal): return String(strVal) + ~Whitespaces

def Identifier(keywords):
    @Parser
    def run(inp):
        idparser = Join % ( CharSatisfy(str.isalpha) / Char("_") + 
                            Many(CharSatisfy(str.isalnum) | Char("_")) 
                          )
                        
        res = idparser.run(inp)
        if res.val[0] not in keywords:
            return res
    return run

def Between(begin, end, psr): 
    return ~Terminal(begin) + psr + ~Whitespaces + ~Terminal(end)

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
