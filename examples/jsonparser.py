from parsyc import *

jsNumber = float % Regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
jsTrue   = Terminal("true" ).to(True)
jsFalse  = Terminal("false").to(False)
jsNull   = Terminal("null" ).to(None)
jsEscChr = ~Char("\\") + (
    Char("\\")         | 
    Char('"')          | 
    Char('b').to('\b') | 
    Char('f').to('\f') | 
    Char('n').to('\n') | 
    Char('r').to('\r') | 
    Char('t').to('\t') |
    Regex(r'u[0-9a-fA-F]{4}').map(lambda s: chr(int(s[1:], 16)))
) 
jsString = "".join @ Between(~Char('"'), ~Char('"'), jsEscChr | AnyChar)
jsArray  = list @ forward(lambda:
    BetweenStr("[", "]", SepBy(jsVal, ~Terminal(",")))
)
jsObject = dict @ forward(lambda:
    BetweenStr("{", "}", SepBy(Tuple @ (jsString + ~Terminal(":") + jsVal), 
                            ~Terminal(",")
                            ))
)
jsVal = jsNumber | jsString | jsObject | jsArray | jsTrue | jsFalse | jsNull
jsonP = ~Whitespaces + jsObject + ~Whitespaces

################################################################################

testjson = """
{
    "object": {
        "title": "new\\nline",
		"Div": {
            "title": "\uffff",
			"item": { "val": { "ID": "#0", "Def": { "float": -1.6e2 } } }
        }
    },
    "list": [
        "Hello", 
        ["nested", "array"], 
        { "nested": { "object": [1, 2, "Hi"] }}
    ]
}
"""

print(jsonP.parse(testjson))