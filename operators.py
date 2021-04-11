from parser import Parser, ParserResult
from functor import Functor

########################### Functors to wrap data ##############################

Join = lambda *iter: "".join(iter)
ToInt = int

########################### Basic parsers ######################################


def Times(psr, mn, mx=-1):
    if (mx and mx < 0): 
        mx = mn
    @Parser
    def run(inp):
        count = 0
        res = ParserResult(inp, ()) 
        while True:
            temp = psr.run(res.rest)
            if not temp:
                if count >= mn:
                    return res
                return ParserResult.reject()
            count += 1
            if (mx is not None and count > mx):
                return res
            res = ParserResult(temp.rest, res.ans + temp.ans)
    return run

def Many(psr):      return Times(psr, 0, None)
def Some(psr):      return Times(psr, 1, None)
def Optional(psr):  return Times(psr, 0, 1)


@Parser
def AnyChar(inp):
    if len(inp)>0:
        return ParserResult(inp[1:],(inp[0],))
    return ParserResult.reject()

def Char(char):
    @Parser
    def run(inp):
        if len(inp)>0 and inp[0]==char:
            return ParserResult(inp[1:],(inp[0],))
        return ParserResult.reject()
    return run

def CharSatisfy(condition):
    @Parser
    def run(inp):
        if len(inp)>0 and condition(inp[0]):
            return ParserResult(inp[1:],(inp[0],))
        return ParserResult.reject()
    return run

@Parser
def EOF(inp):
    if len(inp)==0:
        return ParserResult(inp,())
    return ParserResult.reject()

def String(strVal):
    @Parser
    def run(inp):
        if inp.startswith(strVal):
            return ParserResult(inp[len(strVal):], (strVal,))
        return ParserResult.reject()
    return run

Whitespace = String(" ") | String("\n") | String("\t")
Whitespaces = Many(Whitespace)

Digit = CharSatisfy(str.isdigit)
Integer = ToInt % ( Join % (Many(String("-")|String("+")) + Many(Digit) ))

def Terminal(strVal): return String(strVal) + ~Whitespaces

def Identifier(keywords):
    @Parser
    def run(inp):
        idparser = Join [[ CharSatisfy(str.isalpha) + 
                           Many(CharSatisfy(str.isalnum) | Char("_")) 
                        ]]
        res = idparser.run(inp)
        if not res or res.ans[0] in keywords:
            return ParserResult.reject()
        return res
    return run

def Between(begin, end, psr): 
    return ~Terminal(begin) + psr + ~Whitespaces + ~Terminal(end)

def ChainL1(operator, operand):
    @Parser
    def run(inp):
        res = operand.run(inp)
        if not res: return ParserResult.reject()
        
        def more(res):
            op = operator.run(res.rest)
            if not op: return res
            b = operand.run(op.rest)
            if not b: return res

            newRes = ParserResult(b.rest, (op.ans[0](*(res.ans + b.ans)),))
            return more(newRes)
        
        return more(res)
    return run
