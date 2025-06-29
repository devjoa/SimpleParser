'''
MIT License

Copyright (c) 2025 Johan Öberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

class SimpleParser:
    from typing import NamedTuple
    from collections import deque

    class Token(NamedTuple):
        type: str
        value: str


    def __init__(self, top_grammar, token_type=str, **kwargs):
        self._grammar = self._builder(top_grammar, token_type)
        self._error_filter = lambda v: type(v) is token_type

        self._error_string = kwargs.pop("error_string",
                                        lambda t,el: f'error: unexpected {t.type} type value: "{t.value}", expected type [{",".join(el)}]')
        self._rule_constructor = kwargs.pop("rule_constructor",
                                            lambda type_,value_,token_list_: token_list_[-1]._replace(type=type_, value=value_))
        if kwargs:
            raise TypeError(f'{__name__}() got an unexpected keyword argument \'{"', '".join(kwargs.keys())}\'')


    def parse(self, tokens):
        from copy import copy
        def __eof():
            pass

        tokens = list(tokens)

        ast_stack = [tokens[0]]
        index_stack = [1]
        grammar_stack = [self._grammar]
        while grammar_stack:

            g = grammar_stack[-1]
            if g is None:
                return ast_stack[0].value
            t = ast_stack[-1].type

            if t in g: # Shift
                i = index_stack[-1]
                if i < len(tokens): 
                    ast_stack.append(tokens[i])
                else:
                    ast_stack.append(SimpleParser.Token(type=__eof, value=None))
                grammar_stack.append(g[t])
                index_stack.append(i+1)

            else: # Reduce
                g = grammar_stack.pop()
                index_stack.pop()
                vtoken = ast_stack.pop()
                vgrama = g
                while not None in g:
                    g = grammar_stack.pop()
                    index_stack.pop()
                    ast_stack.pop()
                    if not grammar_stack:
                        te = filter(self._error_filter, vgrama.keys())
                        raise Exception(self._error_string(vtoken, te))
                i = index_stack[-1]

                rule = g[None]
                nb = rule[2] # Number of items to consume
                l = self.deque()
                for _ in range(0,nb):
                    if _:
                        grammar_stack.pop()
                    index_stack.pop()
                    l.appendleft(ast_stack.pop())

                value = rule[1](self._NodeList(l)) 
                t = self._rule_constructor(rule[0], value, l)
                ast_stack.append(t)
                index_stack.append(i)



    @staticmethod
    def __symbol(v):
        if callable(v):
            return v.__name__
        elif v is None:
            return None
        else:
            return f'"{v}"'

    def dump(self):
        def _dump_rule_set(rule, indent="", prev=[]):
            istr=" |"
            count = len(rule)
            for k,v in rule.items():
                count -= 1
                if not count:
                    istr = "  "
                if type(v) is dict:
                    if v not in prev:
                        prev.append(v)
                        print(indent, "+", self.__symbol(k))
                        _dump_rule_set(v, indent+istr, prev)
                        #prev.pop()
                    else:
                        print(indent, "+", self.__symbol(k), "(repeated)")
                elif v is None:
                    print(indent, "+", self.__symbol(k), "->", v)
                else:
                    print(indent, "+", self.__symbol(k), "->", v[0].__name__, f'({v[2]})')

        _dump_rule_set(self._grammar)

    @staticmethod
    def _builder(top_grammar, token_type=str):
        from collections import deque
        _result = dict()

        def _root(grammar):
            @grammar([top_grammar])
            def _(ast):
                return ast[0]

        builder = deque( [( _result, [ ("#", { _root: None }) ] )] )

        rule_dict = {} # The single rule
        rule_name_cache = {} # Complete rules

        while builder:
            target, grammar = builder.popleft()
            meta_target = dict()
            expanded = set()
            rules = deque(grammar)
            while rules:
                name, rule = rules.popleft()
                index = 0
                for k,v in rule.items():
                    if callable(k) and k not in expanded:
                        t = None
                        expanded.add(k)
                        if k in rule_dict:
                            t = rule_dict.get(k)
                        else:
                            gr = SimpleParser._GrammarRule(k)
                            k(gr)
                            t = gr.rule()
                            rule_dict[k] = t
                        rules.append((k.__name__, t ))
                    if type(v) is dict:
                        t = meta_target.setdefault(k, [])
                        t.append((f"{name}'{index}", v))
                    else:
                        assert(k not in meta_target)
                        meta_target[k] = v 
                    index += 1
                # end for k,v
            # end while rules
            for k,v in meta_target.items():
                if type(v) is list:
                    super_rule_name = ";".join(sorted([ _[0] for _ in v ]))
                    if super_rule_name not in rule_name_cache:
                        _ = dict()
                        builder.append( ( _, v ))
                        rule_name_cache[super_rule_name] = _

                    target[k] = rule_name_cache[super_rule_name]
                else:
                    target[k] = v
            # end for k,v in meta_target.items()
        # end while builder

        return _result
 
    class _GrammarRule:
        def __init__(self, target):
            self._rule = dict() 
            self._target = target

        def rule(self):
            return self._rule

        def __call__(self, *rules):
            def _rule_decorator(func):
                for rule in rules:
                    t = self._rule
                    count = 0
                    for r in rule:
                        count += 1
                        if r not in t:
                            t[r] =  dict()
                        t = t[r] 
                    else:
                        t[None] = (self._target, func, count)

                return func
            return _rule_decorator

    class _NodeList:
        def __init__(self, nodes):
            self._nodes = nodes

        def gettoken(self, key):
            return self._nodes.__getitem__(key).token

        def getvalue(self, key):
            return self._nodes.__getitem__(key).value


        def get(self, key):
            return self._nodes.__getitem__(key)

        def __len__(self):
            return self._nodes.__len__()

        def __getitem__(self, key):
            return self.getvalue(key)



