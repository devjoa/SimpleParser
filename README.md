SimpleParser
============

Introduction
------------
SimpleParser is a light-weight Context-Free Grammar LL(k) top-down parser generator
 module written in pure Python3.  The word *simple* refer to a simple to use framework
to create a parser in a pythonic [YACC](https://en.wikipedia.org/wiki/Yacc)
way with minimal overhead. The word *simple* does not refer to that your parse tree has
to be simple or the underlying implementation of the module is simple.

The main motivation of this library is to simplify creation of Domain-Specific Languages (DSL)
that I think python was missing.

The parser doesn't contain a tokenizer/lexer, this you have to write yourself, but the
Python manual provides a simple example that is a good start for most cases 
[re - Writing a Tokenizer](https://docs.python.org/3/library/re.html#writing-a-tokenizer).
You just need to use `SimpleParser.Token` class instead.

How To Create a Parse Tree
--------------------------

Your grammar is defined using functions as rule targets, and decorators and subfunctions
 to define rule definitions. An example of this is as follow:

```python
def my_root_rule(grammar):
    @grammar([my_leaf_rule])
    def _(ast):
        return [ ast[0], ]  # Return it as a list

    @grammar([my_root_rule, ",", my_leaf_rule])
    def _(ast):
        ast[0].append(ast[2] # Append value to list
        return ast[0] 

def my_leaf_rule(grammar):
    @grammar(["NUMBER", "+", "NUMBER"],
             ["NUMBER", "-", "NUMBER"])
    def _(ast):
        if ast.gettoken(1) == "+":
            return ast[0] + ast[2]
        else:
            return ast[0] - ast[2]

grammar = SimpleParser(my_root_rule)
```

When the parse tree is generated, the `my_root_rule` is called from the `SimpleParser` grammar builder.
There is the decorator `@grammar` used to define the rule definitions. In the @grammar decorator you
define one or more lists of rules for the function to be invoked. The function declared after the 
decorator will be the one that is inoked when one of the rules are satisfied.
In the function of the decorator,
you describe what you want to do with the token. By default, the index operator of the `ast` parameter
is the value, but if you call `ast.gettoken(index)`, `ast.getvalue(index)`, or `ast.get(indexI` you will
get either the token, the value (same as index) or the whole token itself.

You must always return a value to the upper layer of the same or a refined type.


Module Contents
---------------

`simpleparser.SimpleParser(self, top_grammar, token_type=str, error_string=None)`

TBD

### Example
```python
from simpleparser import SimpleParser
import re

def tokenize(code):
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
        ('PLUS',        r'[+]'),      # Arithmetic operators
        ('MINUS',        r'[\-]'),      # Arithmetic operators
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID' and value in keywords:
            kind = value
        elif kind == 'NEWLINE':
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected input')

        yield SimpleParser.Token(kind, value)


def AdditiveExpression(grammar):
    @grammar([UnaryExpression])
    def _(ast):
        return ast[0]

    @grammar([AdditiveExpression, 'PLUS', UnaryExpression])
    def _(ast):
        return ast[0] + ast[2]

    @grammar([AdditiveExpression, 'MINUS', UnaryExpression])
    def _(ast):
        return ast[0] - ast[2]

def UnaryExpression(grammar):
    @grammar(["NUMBER"])
    def _(ast):
        return ast[0]

    @grammar(['MINUS', "NUMBER"])
    def _(ast):
        return -ast[1]

    @grammar(['PLUS', "NUMBER"])
    def _(ast):
        return ast[1]

grammar = SimpleParser(AdditiveExpression)

statements = '''
        - 1 + 2 + -3 + + 4 - 5 - -6 - +7 + 8
'''
ast = grammar.parse(tokenize(statements))
print(ast) # print 8
```


