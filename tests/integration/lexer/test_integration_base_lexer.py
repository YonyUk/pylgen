from typing import List

import pytest
import re
from string import digits,ascii_letters
from random import choices,randint

from pylgen.common.table import Table
from pylgen.common.types import Symbol
from pylgen.common.enums import TokenType
from pylgen.lexer.base_lexer import BaseLexer
from pylgen.lexer.lexer import Lexer
from pylgen.automaton.automaton import NFA,DFA,State,create_dfa,get_words_automaton_with_value
from pylgen.analysis.lexical import LexicalRule

class TokenTypeTestEnum(TokenType):
    NUMBER = 'NUMBER'
    KEYWORD = 'KEYWORD'
    VARIABLE = 'VARIABLE'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    GARBAGE = 'GARBAGE'

def get_symbol_function(type_:TokenTypeTestEnum,text:str) -> Symbol:
    if type_ == TokenTypeTestEnum.NUMBER:
        return Symbol('number',True)
    if type_ == TokenTypeTestEnum.VARIABLE:
        return Symbol('variable',True)
    if type_ == TokenTypeTestEnum.SYMBOL:
        return Symbol(text,True)
    if type_ == TokenTypeTestEnum.OPERATOR:
        return Symbol(text,True)
    return Symbol(text,True)

class TestIntegrationBaseLexer:

    @pytest.fixture
    def keywords(self) -> List[str]:
        return ['print','input','len']
    
    @pytest.fixture
    def symbols(self) -> List[str]:
        return ['(',')']
    
    @pytest.fixture
    def operators(self) -> List[str]:
        return ['*','+']

    @pytest.fixture
    def ignore_dfa(self):
        dfa = DFA('start','start',{' ','\n','\t'},True)
        dfa += dfa.start_state,' ',dfa.start_state
        dfa += dfa.start_state,'\n',dfa.start_state
        dfa += dfa.start_state,'\t',dfa.start_state
        return dfa
    
    @pytest.fixture
    def ignore_pattern(self):
        return r'\n|\t| '

    @pytest.fixture
    def number_dfa(self) -> DFA:
        start = State('start','start')
        q0 = State('q0',TokenTypeTestEnum.NUMBER,True)

        table = Table()
        for digit in digits:
            table['start',digit] = 'q0'
            table['q0',digit] = 'q0'
        
        dfa = create_dfa({start,q0},table,start.id,set(digits))
        return dfa
    
    @pytest.fixture
    def keyword_nfa(self,keywords:list[str]) -> NFA:
        return get_words_automaton_with_value(keywords,TokenTypeTestEnum.KEYWORD,True)
    
    @pytest.fixture
    def symbol_dfa(self,symbols:List[str]) -> NFA:
        return get_words_automaton_with_value(symbols,TokenTypeTestEnum.SYMBOL,True)
    
    @pytest.fixture
    def operator_dfa(self,operators:List[str]) -> NFA:
        return get_words_automaton_with_value(operators,TokenTypeTestEnum.OPERATOR,True)

    @pytest.fixture
    def variable_dfa(self) -> DFA:
        dfa = DFA('start','start',set(ascii_letters+digits+'_'))
        final = State('final',TokenTypeTestEnum.VARIABLE,True)
        
        for char in ascii_letters + '_':
            dfa.add_transition(dfa.start_state,final,char)
            dfa.add_transition(final,final,char)
        
        for digit in digits:
            dfa.add_transition(final,final,digit)
        
        return dfa

    def test_lexer_initialization_1_1(self,number_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        dfa = lexer.dfa
        for _ in range(100):
            size = randint(1,20)
            number = choices(digits,k=size)
            assert dfa.accept(number)
        
        assert not dfa.accept([])

    def test_lexer_initialization_1_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer.initialize()

        dfa = lexer.dfa
        for _ in range(100):
            size = randint(1,20)
            number = choices(digits,k=size)
            assert dfa.accept(number)
        
        assert not dfa.accept([])
    
    def test_lexer_initialization_2_1(self,keyword_nfa:NFA,keywords:list[str],ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.KEYWORD] = keyword_nfa
        lexer.initialize()

        dfa = lexer.dfa
        for word in keywords:
            assert dfa.accept(list(word))
        
        for _ in range(100):
            size = randint(1,20)
            word = choices(ascii_letters,k=size)
            if not ''.join(word) in keywords:
                assert not dfa.accept(word)
            else:
                assert dfa.accept(word)
    
    def test_lexer_initialization_2_2(self,keywords:list[str],ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.KEYWORD] = '|'.join(keywords)
        lexer.initialize()

        dfa = lexer.dfa
        for word in keywords:
            assert dfa.accept(list(word))
        
        for _ in range(100):
            size = randint(1,20)
            word = choices(ascii_letters,k=size)
            if not ''.join(word) in keywords:
                assert not dfa.accept(word)
            else:
                assert dfa.accept(word)
    
    def test_lexer_initialization_3_1(self,number_dfa:DFA,keyword_nfa:NFA,keywords:list[str],ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer[1,TokenTypeTestEnum.KEYWORD] = keyword_nfa
        lexer.initialize()

        dfa = lexer.dfa
        for _ in range(100):
            size = randint(1,20)
            number = choices(digits,k=size)
            assert dfa.accept(number)
        
        assert not dfa.accept([])

        for word in keywords:
            assert dfa.accept(list(word))
        
        for _ in range(100):
            size = randint(1,20)
            word = choices(ascii_letters,k=size)
            if not ''.join(word) in keywords:
                assert not dfa.accept(word)
            else:
                assert dfa.accept(word)

    def test_lexer_initialization_3_2(self,keywords:list[str],ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeTestEnum.KEYWORD] = '|'.join(keywords)
        lexer.initialize()

        dfa = lexer.dfa
        for _ in range(100):
            size = randint(1,20)
            number = choices(digits,k=size)
            assert dfa.accept(number)
        
        assert not dfa.accept([])

        for word in keywords:
            assert dfa.accept(list(word))
        
        for _ in range(100):
            size = randint(1,20)
            word = choices(ascii_letters,k=size)
            if not ''.join(word) in keywords:
                assert not dfa.accept(word)
            else:
                assert dfa.accept(word)
        
    def test_lexer_tokenization_1_1(self,number_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        tokens = list(lexer.tokens)
        
        assert len(tokens) == 0

    def test_lexer_tokenization_1_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer.initialize()

        tokens = list(lexer.tokens)
        
        assert len(tokens) == 0

    def test_lexer_tokenization_2_1(self,number_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        text = '''1 0 01 10 35 353
3534 172
1238 23819 238932
'''
        lexer.load_text(text)

        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (3,1),
            (5,1),
            (8,1),
            (11,1),
            (14,1),
            (1,2),
            (6,2),
            (1,3),
            (6,3),
            (12,3)
        ]
        assert len(tokens) == 11
        assert all(map(lambda token:token.type==TokenTypeTestEnum.NUMBER,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]

    def test_lexer_tokenization_2_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer.initialize()

        text = '''1 0 01 10 35 353
3534 172
1238 23819 238932
'''
        lexer.load_text(text)

        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (3,1),
            (5,1),
            (8,1),
            (11,1),
            (14,1),
            (1,2),
            (6,2),
            (1,3),
            (6,3),
            (12,3)
        ]
        assert len(tokens) == 11
        assert all(map(lambda token:token.type==TokenTypeTestEnum.NUMBER,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]
    
    def test_lexer_tokenization_3_1(self,keyword_nfa:NFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.KEYWORD] = keyword_nfa
        lexer.initialize()

        text = '''print input
len input print
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (7,1),
            (1,2),
            (5,2),
            (11,2)
        ]
        assert len(tokens) == 5
        assert all(map(lambda token:token.type==TokenTypeTestEnum.KEYWORD,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]

    def test_lexer_tokenization_3_2(self,keywords:list[str],ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.KEYWORD] = '|'.join(keywords)
        lexer.initialize()

        text = '''print input
len input print
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (7,1),
            (1,2),
            (5,2),
            (11,2)
        ]
        assert len(tokens) == 5
        assert all(map(lambda token:token.type==TokenTypeTestEnum.KEYWORD,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]
    
    def test_lexer_tokenization_4_1(self,variable_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.VARIABLE] = variable_dfa
        lexer.initialize()

        text = '''var var1 _var2
var_3 var_4_ _var_5 nad_2_nad_12_token
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (5,1),
            (10,1),
            (1,2),
            (7,2),
            (14,2),
            (21,2)
        ]
        assert len(tokens) == 7
        assert all(map(lambda token:token.type==TokenTypeTestEnum.VARIABLE,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]

    def test_lexer_tokenization_4_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.VARIABLE] = '[a-zA-Z_]\\w*'
        lexer.initialize()

        text = '''var var1 _var2
var_3 var_4_ _var_5 nad_2_nad_12_token
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        pos = [
            (1,1),
            (5,1),
            (10,1),
            (1,2),
            (7,2),
            (14,2),
            (21,2)
        ]
        assert len(tokens) == 7
        assert all(map(lambda token:token.type==TokenTypeTestEnum.VARIABLE,tokens))
        for i in range(len(tokens)):
            assert tokens[i].column == pos[i][0]
            assert tokens[i].line == pos[i][1]
    
    def test_lexer_tokenization_5_1(self,keyword_nfa:NFA,number_dfa:DFA,variable_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.KEYWORD] = keyword_nfa
        lexer[1,TokenTypeTestEnum.VARIABLE] = variable_dfa
        lexer[2,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        text = '''print my_var len
123 _var_2_in input var05
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.VARIABLE,
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.VARIABLE,
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.VARIABLE
        ]
        assert len(tokens) == 7
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            match_:re.Match = re.search(token.text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line

    def test_lexer_tokenization_5_2(self,keywords:list[str],ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.KEYWORD] = '|'.join(keywords)
        lexer[1,TokenTypeTestEnum.VARIABLE] = '[a-zA-Z_]\\w*'
        lexer[2,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer.initialize()

        text = '''print my_var len
123 _var_2_in input var05
'''

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.VARIABLE,
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.VARIABLE,
            TokenTypeTestEnum.KEYWORD,
            TokenTypeTestEnum.VARIABLE
        ]
        assert len(tokens) == 7
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            match_:re.Match = re.search(token.text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line
    
    def test_lexer_tokenization_6_1(self,number_dfa:DFA,symbol_dfa:NFA,operator_dfa:NFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer[1,TokenTypeTestEnum.SYMBOL] = symbol_dfa
        lexer[2,TokenTypeTestEnum.OPERATOR] = operator_dfa

        lexer.initialize()
        text = "(8*5)"

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.SYMBOL,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.OPERATOR,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.SYMBOL
        ]
        assert len(tokens) == 5
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            t_text = f'\\{token.text}' if token.text in '()*+' else token.text
            match_:re.Match = re.search(t_text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line

    def test_lexer_tokenization_6_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeTestEnum.SYMBOL] = '\\(|\\)'
        lexer[2,TokenTypeTestEnum.OPERATOR] = '\\*|\\+'

        lexer.initialize()
        text = "(8*5)"

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.SYMBOL,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.OPERATOR,
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.SYMBOL
        ]
        assert len(tokens) == 5
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            t_text = f'\\{token.text}' if token.text in '()*+' else token.text
            match_:re.Match = re.search(t_text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line

    def test_lexer_tokenization_7_1(self,number_dfa:DFA,symbol_dfa:NFA,operator_dfa:NFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer[1,TokenTypeTestEnum.SYMBOL] = symbol_dfa
        lexer[2,TokenTypeTestEnum.OPERATOR] = operator_dfa

        lexer.initialize()
        text = "9+ 2"

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.OPERATOR,
            TokenTypeTestEnum.NUMBER,
        ]
        assert len(tokens) == 3
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            t_text = f'\\{token.text}' if token.text in '()*+' else token.text
            match_:re.Match = re.search(t_text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line

    def test_lexer_tokenization_7_2(self,ignore_pattern:str):
        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeTestEnum.SYMBOL] = '\\(|\\)'
        lexer[2,TokenTypeTestEnum.OPERATOR] = '\\*|\\+'

        lexer.initialize()
        text = "9+ 2"

        lexer.load_text(text)
        tokens = list(lexer.tokens)
        types = [
            TokenTypeTestEnum.NUMBER,
            TokenTypeTestEnum.OPERATOR,
            TokenTypeTestEnum.NUMBER,
        ]
        assert len(tokens) == 3
        for index,token in enumerate(tokens):
            assert token.type == types[index]
            t_text = f'\\{token.text}' if token.text in '()*+' else token.text
            match_:re.Match = re.search(t_text,text) # type: ignore
            pos = match_.start()
            column = pos - text.rindex('\n',0,pos) if '\n' in text[:pos] else pos + 1
            line = 1 + text.count('\n',pos) if '\n' in text[:pos] else 1
            assert token.column == column
            assert token.line == line
    
    def test_lexer_tokenization_with_error_collecting_1(self,ignore_pattern:str):

        class IntegerRule(LexicalRule):

            def __init__(self) -> None:
                super().__init__('integers must star with a non-zero digit or be zero')
            
            def _check(self, text: str):
                return str(int(text)) == text

        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer.add_rule(TokenTypeTestEnum.NUMBER,IntegerRule())

        lexer.initialize()

        text = '010 23 00000 245 0 003'
        lexer.load_text(text)
        for _ in lexer.tokens: pass

        errors = [(1,1),(1,8),(1,20)]
        assert len(lexer.errors) != 0
        for error in lexer.errors:
            assert (error.line,error.column) in errors

    def test_lexer_tokenization_with_error_collecting_2(self,ignore_pattern:str):

        class IntegerRule(LexicalRule):

            def __init__(self) -> None:
                super().__init__('integers must star with a non-zero digit or be zero')
            
            def _check(self, text: str):
                return str(int(text)) == text
        
        class VariableRule(LexicalRule):

            def __init__(self) -> None:
                super().__init__('variables names can\'t star with a number')
            
            def _check(self, text: str):
                return not text[0].isdigit()

        lexer = Lexer(get_symbol_function,ignore_pattern)
        lexer[0,TokenTypeTestEnum.NUMBER] = '\\d+'
        lexer[1,TokenTypeTestEnum.VARIABLE] = '\\w+'
        
        lexer.add_rule(TokenTypeTestEnum.NUMBER,IntegerRule())
        lexer.add_rule(TokenTypeTestEnum.VARIABLE,VariableRule())

        lexer.initialize()

        text = '010 23 00000 245 0 003 var_1 _var2 0_var 1nada'

        lexer.load_text(text)
        for _ in lexer.tokens: pass

        errors = [(1,1),(1,8),(1,20),(1,36),(1,42)]
        assert len(lexer.errors) != 0
        for error in lexer.errors:
            assert (error.line,error.column) in errors