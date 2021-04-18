# Parsyc: Yet another combinatorial parser library.

Heavily inspired by the `Parsec` library from Haskell, this library allows you to
use certain operators to emulate `fmap` like functionality, composing functions with
Parser objects. For instance:

```py
p = str.upper % String("hello world")
```

constructs a parser object that matches the literal text `hello world` and then returns
the result of applying the `str.upper` function to it (so `'HELLO WORLD'`). It allows
you do chain these together, so here would be a parser for an integer:

```py
integerP = int % Regex(r'[-+]?[0-9]+')
# integerP.parse("-37") --> -37
# integerP.parse("bad") --> None
```
