import unittest
from src.simpleparser.simpleparser import SimpleParser



class Test1(unittest.TestCase):
    def test_list_int(self):
        import re

        def tokenize(code):
            keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
            token_specification = [
                ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
                ('ASSIGN',   r':='),           # Assignment operator
                ('END',        r';'),            # Statement terminator
                ('ID',       r'[A-Za-z]+'),    # Identifiers
                ('BPAREN',        r'[(]'),      # Arithmetic operators
                ('EPAREN',        r'[)]'),      # Arithmetic operators
                ('PLUS',        r'[+]'),      # Arithmetic operators
                ('MINUS',        r'[\-]'),      # Arithmetic operators
                ('MUL',        r'[*]'),      # Arithmetic operators
                ('DIV',        r'[/]'),      # Arithmetic operators
                ('NEWLINE',  r'\n'),           # Line endings
                ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
                ('MISMATCH', r'.'),            # Any other character
            ]
            tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
            line_num = 1
            line_start = 0
            for mo in re.finditer(tok_regex, code):
                kind = mo.lastgroup
                value = mo.group()
                column = mo.start() - line_start
                if kind == 'NUMBER':
                    value = float(value) if '.' in value else int(value)
                elif kind == 'ID' and value in keywords:
                    kind = value
                elif kind == 'NEWLINE':
                    line_start = mo.end()
                    line_num += 1
                    continue
                elif kind == 'SKIP':
                    continue
                elif kind == 'MISMATCH':
                    raise RuntimeError(f'{value!r} unexpected on line {line_num}')

                yield SimpleParser.Token(kind, value)


        def Statement(grammar):
            @grammar(['ID', 'ASSIGN', AdditiveExpression, 'END'])
            def _(ast):
                return { ast[0]: ast[2] }

        def AdditiveExpression(grammar):
            @grammar([MultiplicativeExpression])
            def _(ast):
                return ast[0]

            @grammar([AdditiveExpression, 'PLUS', MultiplicativeExpression])
            def _(ast):
                return ast[0] + ast[2]

            @grammar([AdditiveExpression, 'MINUS', MultiplicativeExpression])
            def _(ast):
                return ast[0] - ast[2]


        def MultiplicativeExpression(grammar):
            @grammar([UnaryExpression])
            def _(ast):
                return ast[0]

            @grammar([MultiplicativeExpression, 'MUL', UnaryExpression])
            def _(ast):
                return ast[0] * ast[2]

            @grammar([MultiplicativeExpression, 'DIV', UnaryExpression])
            def _(ast):
                return ast[0] / ast[2]


        def UnaryExpression(grammar):
            @grammar([PrimaryExpression])
            def _(ast):
                return ast[0]

            @grammar(['MINUS', PrimaryExpression])
            def _(ast):
                return -ast[1]

            @grammar(['PLUS', PrimaryExpression])
            def _(ast):
                return ast[1]


        def PrimaryExpression(grammar):
            @grammar(['NUMBER'])
            def _(ast):
                return ast[0]

            @grammar(['BPAREN', AdditiveExpression, 'EPAREN'])
            def _(ast):
                return ast[1]


        statements = '''
                VALUE := 1 + 2 * 3 - (1 - -2) * 3;
        '''

        grammar = SimpleParser(Statement)

        ast = grammar.parse(tokenize(statements))
        self.assertEqual(ast['VALUE'], -2)



class Test2(unittest.TestCase):
    def test_list_int(self):
        import re

        def tokenize(code):
            keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
            token_specification = [
                ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
                ('ASSIGN',   r':='),           # Assignment operator
                ('END',        r';'),            # Statement terminator
                ('COMMA',        r'\,'),            # Statement terminator
                ('ID',       r'[A-Za-z][A-Za-z0-9]*'),    # Identifiers
                ('BPAREN',        r'[(]'),      # Arithmetic operators
                ('EPAREN',        r'[)]'),      # Arithmetic operators
                ('PLUS',        r'[+]'),      # Arithmetic operators
                ('MINUS',        r'[\-]'),      # Arithmetic operators
                ('MUL',        r'[*]'),      # Arithmetic operators
                ('DIV',        r'[/]'),      # Arithmetic operators
                ('NEWLINE',  r'\n'),           # Line endings
                ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
                ('MISMATCH', r'.'),            # Any other character
            ]
            tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
            line_num = 1
            line_start = 0
            for mo in re.finditer(tok_regex, code):
                kind = mo.lastgroup
                value = mo.group()
                column = mo.start() - line_start
                if kind == 'NUMBER':
                    value = float(value) if '.' in value else int(value)
                elif kind == 'ID' and value in keywords:
                    kind = value
                elif kind == 'NEWLINE':
                    line_start = mo.end()
                    line_num += 1
                    continue
                elif kind == 'SKIP':
                    continue
                elif kind == 'MISMATCH':
                    raise RuntimeError(f'{value!r} unexpected on line {line_num}')

                yield SimpleParser.Token(kind, value)


        def Statement(grammar):
            @grammar(['ID', 'ASSIGN', Expression, 'END'])
            def _(ast):
                return { ast[0]: ast[2] }

        def Expression(grammar):
            @grammar(["NUMBER"],
                     ["ID"])
            def _(ast):
                return ast[0]

            @grammar(["NUMBER", "COMMA", ExpressionList],
                     ["ID", "COMMA", ExpressionList])
            def _(ast):
                ast[2].insert(0, ast[0])
                return ast[2]

        def ExpressionList(grammar):
            @grammar(["NUMBER"],
                     ["ID"])
            def _(ast):
                return [ ast[0] ]

            @grammar([ "NUMBER", "COMMA", ExpressionList ],
                     [ "ID", "COMMA", ExpressionList])
            def _(ast):
                ast[2].insert(0,ast[0])
                return ast[2]

        statements = '''
                VALUE1 := 1,2,3,4,5,6,seven;
        '''

        grammar = SimpleParser(Statement)


        ast = grammar.parse(tokenize(statements))
        self.assertEqual(ast['VALUE1'], [1,2,3,4,5,6,"seven"])

        statements = '''
                VALUE2 := one;
        '''
        ast = grammar.parse(tokenize(statements))
        self.assertEqual(ast['VALUE2'], "one")

        statements = '''
               error := ,; 
        '''
        with self.assertRaises(Exception) as context:
            ast = grammar.parse(tokenize(statements))

        self.assertIn('error: unexpected COMMA type value: ",", expected type [NUMBER,ID]', str(context.exception))

class TestExample(unittest.TestCase):
    def test_list_int(self):
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

        statements = '''
                - 1 + 2 + -3 + + 4 - 5 - -6 - +7 + 8
        '''

        grammar = SimpleParser(AdditiveExpression)

        ast = grammar.parse(tokenize(statements))
        self.assertEqual(ast, 4)
        



if __name__ == '__main__':
    unittest.main()
