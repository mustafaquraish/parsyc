import unittest

from parser import Parser
from operators import *

import string

class TestBasicParsers(unittest.TestCase):

    def check(self, res, expected):
        self.assertIsNotNone(res)
        self.assertEqual(res, expected)

    def test_anychar(self):
        p = AnyChar
        self.check(p.parse("AGHK"), "A")
        self.check(p.parse("BGHK"), "B")
        self.check(p.parse("CGHK"), "C")
        self.assertIsNone(p.parse(""))

    def test_char(self):
        p = Char("H")
        for c in string.printable:
            if c == 'H': 
                self.check(p.parse(c), c)
            else:
                self.assertIsNone(p.parse(c))

    def test_satisfychar(self):
        subset = "HGSKNB"
        p = CharSatisfy(lambda c: c in subset)
        for c in string.printable:
            if c in subset: 
                self.check(p.parse(c), c)
            else:
                self.assertIsNone(p.parse(c))

    def test_eof(self):
        p = EOF
        self.assertIsNotNone(p.parse(""))
        self.assertIsNone(p.parse("."))

    def test_string(self):
        p = String("Hello")
        self.check(p.parse("Hello"), "Hello")
        self.assertIsNone(p.parse("Hi"))
        self.assertIsNone(p.parse("hello"))
        self.assertIsNone(p.parse("Hell"))
        self.assertIsNone(p.parse("Hell0"))

    def test_whitespace(self):
        p = Whitespace
        self.check(p.parse(" "), " ")
        self.check(p.parse("\t"), "\t")
        self.check(p.parse("\n"), "\n")
        self.assertIsNone(p.parse("Hi"))

    def test_whitespaces(self):
        p = Whitespaces
        self.check(p.parse("       "), "       ")
        self.check(p.parse("\t\n   \n\tOtherText"), "\t\n   \n\t")
        self.check(p.parse("\n\n\n\nHelloThere"), "\n\n\n\n")
        self.check(p.parse("Hi"), '')   # 0 or more...
        
    def test_terminal(self):
        p = Terminal("String")
        self.check(p.parse("String      \n\t\t"), "String")
        self.check(p.parse("String\n\t\t"), "String")
        self.check(p.parse("String"), "String")
        self.assertIsNone(p.parse("SomethingElse"))
        # Leading whitespaces not handled
        self.assertIsNone(p.parse("  String"))
        self.assertIsNone(p.parse("S t r i n g"))

    def test_identifier(self):
        keywords = ["int", "double", "class", "struct"]
        p = Identifier(keywords)
        self.check(p.parse("hello"), "hello")
        self.check(p.parse("hELLO"), "hELLO")
        self.check(p.parse("hELL012_3"), "hELL012_3")
        self.check(p.parse("Hell012_3"), "Hell012_3")
        self.check(p.parse("_Hell012_3"), "_Hell012_3")
        self.assertIsNone(p.parse("1test"))
        self.assertIsNone(p.parse("?test"))
        self.assertIsNone(p.parse("int"))
        self.assertIsNone(p.parse("class"))
        self.assertIsNone(p.parse("double"))
        self.assertIsNone(p.parse("struct"))

    def test_integer(self):
        p = Integer
        self.check(p.parse("123"), 123)
        self.check(p.parse("-123"), -123)
        self.check(p.parse("+456"), 456)
        self.assertIsNone(p.parse("Hello"))
        self.assertIsNone(p.parse("---"))

class TestCombinator(unittest.TestCase):

    def check(self, res, expected):
        self.assertIsNotNone(res)
        self.assertEqual(res, expected)

    def test_times(self):
        p = Times(Integer + ~Whitespaces, 3)
        self.assertIsNotNone(p.parse("1 2 3 "))
        self.assertIsNotNone(p.parse("123 234 345"))
        self.assertIsNotNone(p.parse("123 234 3"))
        self.assertIsNone(p.parse("123 234"))
        self.assertIsNone(p.parse("123"))
        self.assertIsNone(p.parse(""))

        p = Times(Integer + ~Whitespaces, 6, 10)
        for i in range(20):
            s = "5 " * i
            if 6 <= i <= 10:
                self.check(p.parse(s), (5,)*i)
            elif i < 6:
                self.assertIsNone(p.parse(s))
            else:
                self.check(p.parse(s), (5,)*10)
    
    def test_between(self):
        p = Between("(", ")", Integer)
        self.check(p.parse("(123)"), 123)
        self.check(p.parse("( 123 )    "), 123)
        self.assertIsNone(p.parse("{123}"))
        self.assertIsNone(p.parse("(123"))
        self.assertIsNone(p.parse("123)"))


        p = Between("{", "}", Identifier([]))
        self.check(p.parse("{hello}"), "hello")
        self.check(p.parse("{ hELLO  } "), "hELLO")
        self.assertIsNone(p.parse("(hello)"))

    def test_alternative(self):
        p = String("Hello") | String("Hi") | String("Bye")
        self.check(p.parse("Hello"), "Hello")
        self.check(p.parse("Hi"), "Hi")
        self.check(p.parse("Bye"), "Bye")
        self.assertIsNone(p.parse("Hey"))
        self.assertIsNone(p.parse("hi"))
        self.assertIsNone(p.parse("hello"))

    def test_applicative(self):
        p = String("Hello") + Whitespace + String("World!")
        self.check(p.parse("Hello World!"), ("Hello", " ", "World!"))
        self.assertIsNone(p.parse("Hello World"))
        self.assertIsNone(p.parse("Hello "))

    def test_applicative_alternative(self):
        p = (String("Bye") / String("Hello")) + Whitespace + String("World!")
        self.check(p.parse("Hello World!"), ("Hello", " ", "World!"))
        self.check(p.parse("Bye World!"), ("Bye", " ", "World!"))
        self.assertIsNone(p.parse("Hello World"))
        self.assertIsNone(p.parse("Hello "))
        self.assertIsNone(p.parse("Bye World"))
        self.assertIsNone(p.parse("Bye "))
        self.assertIsNone(p.parse("Bye Hello"))

    def test_ignore(self):
        p = ~String("ignore") + String("hello") + ~String("ignore")
        self.check(p.parse("ignorehelloignore"), "hello")
        self.assertIsNone(p.parse("hello"))
        self.assertIsNone(p.parse("ignorehello"))
        self.assertIsNone(p.parse("helloignore"))

    def test_functor(self):
        Upper = lambda s: s.upper()
        p = Upper % String("test")
        self.check(p.parse("test"), "TEST")
        self.assertIsNone(p.parse("TEST"))

        p = Upper % (Join % (String("hello") + ~Whitespaces + String("world")))
        self.check(p.parse("hello world"), "HELLOWORLD")

        class Dummy:
            def __init__(self, a, b, c):
                self.vals = (a,b,c)
            def __eq__(self, other):
                return self.vals == other.vals

        p = Dummy % Times(Integer + ~Whitespaces, 3)
        self.check(p.parse("1 2 3"), Dummy(1, 2, 3))


if __name__ == '__main__':
    unittest.main()