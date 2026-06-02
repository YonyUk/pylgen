import pytest
from string import digits,ascii_letters
from random import choices,randint

from common.table import Table
from common.types import Symbol
from common.enums import TokenType
from lexer.lexer import BaseLexer
from automaton.automaton import NFA,DFA,State,create_dfa,get_words_automaton

class TokenTypeTestEnum(TokenType):
    NUMBER = 'NUMBER'
    KEYWORD = 'KEYWORD'
    GARBAGE = 'GARBAGE'

def get_symbol_function(type_:TokenTypeTestEnum,text:str):
    if type_ == TokenTypeTestEnum.NUMBER:
        return Symbol('number',True)
    return Symbol(text,True)

class TestIntegrationBaseLexer:

    @pytest.fixture
    def keywords(self) -> list[str]:
        return ['print','input','len']
    
    @pytest.fixture
    def ignore_dfa(self):
        dfa = DFA('start','start',{' ','\n','\t'},True)
        dfa += dfa.start_state,' ',dfa.start_state
        dfa += dfa.start_state,'\n',dfa.start_state
        dfa += dfa.start_state,'\t',dfa.start_state
        return dfa

    @pytest.fixture
    def number_dfa(self) -> DFA:
        start = State('start',TokenTypeTestEnum.NUMBER)

        states_by_digit = {
            '0':State('q0',TokenTypeTestEnum.NUMBER,True),
            '1':State('q1',TokenTypeTestEnum.NUMBER,True),
            '2':State('q2',TokenTypeTestEnum.NUMBER,True),
            '3':State('q3',TokenTypeTestEnum.NUMBER,True),
            '4':State('q4',TokenTypeTestEnum.NUMBER,True),
            '5':State('q5',TokenTypeTestEnum.NUMBER,True),
            '6':State('q6',TokenTypeTestEnum.NUMBER,True),
            '7':State('q7',TokenTypeTestEnum.NUMBER,True),
            '8':State('q8',TokenTypeTestEnum.NUMBER,True),
            '9':State('q9',TokenTypeTestEnum.NUMBER,True)
        }

        table = Table()
        for digit in digits:
            table['start',digit] = states_by_digit[digit].id
            for state in states_by_digit.values():
                table[state.id,digit] = states_by_digit[digit].id
        
        dfa = create_dfa(set(states_by_digit.values()).union({start}),table,start.id,set(digits))
        return dfa
    
    @pytest.fixture
    def keyword_nfa(self,keywords:list[str]) -> NFA:
        return get_words_automaton(keywords)
    
    def test_lexer_initialization_1(self,number_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        dfa = lexer.dfa
        for _ in range(100):
            size = randint(1,20)
            number = choices(digits,k=size)
            assert dfa.accept(number)
        
        assert not dfa.accept([])
    
    def test_lexer_initialization_2(self,keyword_nfa:NFA,keywords:list[str],ignore_dfa:DFA):
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
    
    def test_lexer_initialization_3(self,number_dfa:DFA,keyword_nfa:NFA,keywords:list[str],ignore_dfa:DFA):
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
        
    def test_lexer_tokenization_1(self,number_dfa:DFA,ignore_dfa:DFA):
        lexer = BaseLexer(get_symbol_function,ignore_dfa)
        lexer[0,TokenTypeTestEnum.NUMBER] = number_dfa
        lexer.initialize()

        tokens = list(lexer.tokens)
        
        assert len(tokens) == 0

    def test_lexer_tokenization_2(self,number_dfa:DFA,ignore_dfa:DFA):
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
    
    def test_lexer_tokenization_3(self,keyword_nfa:NFA,ignore_dfa:DFA):
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