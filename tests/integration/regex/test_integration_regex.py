import pytest
import string
import random
import re
from pylgen.regex.engine import RegexEngine
from pylgen.automaton import State,DFA,NFA,create_dfa
from pylgen.common import Table

class TestIntegrationRegex:

    def test_parse_simples_re(self):
        aut = RegexEngine.Parse('a')
        for char in string.printable:
            assert aut.accept([char]) == (char == 'a')
        for _ in range(100):
            k = random.randint(0,50)
            word =random.choices(string.printable,k=k)
            assert aut.accept(word) == (word == ['a'])
    
    @pytest.mark.parametrize("re_exp",[
        '\\d',
        '\\D',
        '\\w',
        '\\W',
        '\\S',
        '\\s'
    ])
    def test_parse_constant(self,re_exp:str):
        aut = RegexEngine.Parse(re_exp)
        for _ in range(1000):
            k = random.randint(0,10)
            word = random.choices(string.printable,k=k)
            assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
    
    @pytest.mark.parametrize("re_exp",[
        'a*',
        'b+',
        'c?',
        'd{0,1}',
        'e{1,1}',
        'f{2,5}',
        'g{10,15}'
    ])
    def test_parse_regex_1(self,re_exp:str):
        aut = RegexEngine.Parse(re_exp)
        for char in string.printable:
            for _ in range(1000):
                word = [char]*random.randint(0,16)
                assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
        for _ in range(1000):
            k = random.randint(0,10)
            word = random.choices(string.printable,k=k)
            assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
    
    @pytest.mark.parametrize("re_exp",[
        '[0-9]',
        '[a-z]',
        '[A-Z]',
        '[a-c]',
        '[x-z]',
        '[a-cA-C]',
        '[0-37-9]'
    ])
    def text_parse_regex_2(self,re_exp:str):
        aut = RegexEngine.Parse(re_exp)
        for _ in range(1000):
            k = random.randint(0,10)
            word = random.choices(string.printable,k=k)
            assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
    
    def test_parse_regex_3(self):
        aut = RegexEngine.Parse('(hello)*')
        assert aut.accept(list('hello'))
        assert aut.accept(list(''))
        assert aut.accept(list('hellohellohellohellohello'))
        assert not aut.accept(list('hell'))
        assert not aut.accept(list('h'))
        assert not aut.accept(list('hellohe'))
        assert not aut.accept(list('hellohellohel'))
        aut = RegexEngine.Parse('(hello)+')
        assert aut.accept(list('hello'))
        assert aut.accept(list('hellohellohellohellohello'))
        assert not aut.accept(list(''))
        assert not aut.accept(list('hell'))
        assert not aut.accept(list('h'))
        assert not aut.accept(list('hellohe'))
        assert not aut.accept(list('hellohellohel'))
        aut = RegexEngine.Parse('(hello)?')
        assert aut.accept(list('hello'))
        assert aut.accept(list(''))
        assert not aut.accept(list('hellohellohellohellohello'))
        assert not aut.accept(list('hell'))
        assert not aut.accept(list('h'))
        assert not aut.accept(list('hellohe'))
        assert not aut.accept(list('hellohellohel'))
    
    @pytest.mark.parametrize("re_exp",[
        '[0-9]*',
        '[0-9]+',
        '[0-9]?',
        '[0-9]{0,1}',
        '[0-9]{0,3}',
        '[0-9]{2,3}',
        '[0-9abc]*',
        '[0-9abc]+',
        '[0-9abc]?',
        '[0-9a-z]*',
        '[0-9a-z]+',
        '[0-9a-z]?',
    ])
    def test_parser_regex_4(self,re_exp:str):
        aut = RegexEngine.Parse(re_exp)
        for _ in range(1000):
            k = random.randint(0,5)
            word = random.choices(string.ascii_letters+string.digits)
            assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
    
    @pytest.mark.parametrize("re_exp,word,should_accept",[
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','1',True),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','110',True),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','.1',True),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','0.129',True),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','1123.12038',True),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','00',False),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','0.0.0',False),
        ('[1-9][0-9]*(\\.[0-9]*)?|0(\\.[0-9]+)?|\\.[0-9]+','..123',False),
        ('hello|world|from|python','hello',True),
        ('hello|world|from|python','world',True),
        ('hello|world|from|python','from',True),
        ('hello|world|from|python','python',True),
        ('hello|world|from|python','nada',False),
        ('hello|world|from|python','nuevo',False),
        ('[a-z]|(hello)+|(play){2,4}','a',True),
        ('[a-z]|(hello)+|(play){2,4}','hello',True),
        ('[a-z]|(hello)+|(play){2,4}','hellohello',True),
        ('[a-z]|(hello)+|(play){2,4}','',False),
        ('[a-z]|(hello)+|(play){2,4}','@',False),
        ('[a-z]|(hello)+|(play){2,4}','z',True),
        ('[a-z]|(hello)+|(play){2,4}','playplay',True),
        ('[a-z]|(hello)+|(play){2,4}','playplayplay',True),
        ('[a-z]|(hello)+|(play){2,4}','playplayplayplay',True),
        ('[a-z]|(hello)+|(play){2,4}','playplayplayplayplay',False),
    ])
    def test_parser_regex_5(self,re_exp:str,word:str,should_accept:bool):
        aut = RegexEngine.Parse(re_exp)
        assert aut.accept(list(word)) == should_accept
    
    def test_parser_regex_6(self):
        aut = RegexEngine.Parse('.')
        for char in string.printable:
            assert aut.accept([char]) == (char != '\n')
    
    def test_parser_regex_7(self):
        aut = RegexEngine.Parse('.*')
        for _ in range(1000):
            k = random.randint(1,20)
            word = random.choices(string.printable,k=k)
            while '\n' in word:
                word.remove('\n')
            assert aut.accept(word)
    
    @pytest.mark.parametrize("re_exp,text,should_accept",[
        ('\\{','{',True),
        ('\\(','(',True),
        ('\\[','[',True),
        ('\\}','}',True),
        ('\\)',')',True),
        ('\\]',']',True),
        ('\\*','*',True),
        ('\\?','?',True),
        ('\\+','+',True),
        ('\\.','.',True),
        ('\\,',',',True),
        ('\\-','-',True),
        ('\\|','a',False),
        ('\\{','b',False),
        ('\\(','c',False),
        ('\\[','d',False),
        ('\\}','e',False),
        ('\\)','f',False),
        ('\\]','g',False),
        ('\\*','h',False),
        ('\\?','i',False),
        ('\\+','j',False),
        ('\\.','k',False),
        ('\\,','l',False),
        ('\\-','m',False),
        ('\\|','n',False),
        ('\\{*','',True),
        ('\\{*','{{',True),
        ('\\{*','{{{',True),
        ('\\{+','{',True),
        ('\\{+','{{',True),
        ('\\{+','{{{',True),
        ('\\(','(',True),
        ('\\[','[',True),
        ('\\}','}',True),
        ('\\)',')',True),
        ('\\]',']',True),
        ('\\*','*',True),
        ('\\?','?',True),
        ('\\+','+',True),
        ('\\.','.',True),
        ('\\,',',',True),
        ('\\-','-',True),
        ('\\|','|',True)
    ])
    def test_parser_regex_8(self,re_exp:str,text:str,should_accept:bool):
        aut = RegexEngine.Parse(re_exp)
        assert aut.accept(list(text)) == should_accept
    
    def test_get_regex_1(self):
        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        t = Table()

        t['q0','a'] = 'q1'

        aut = create_dfa({q0,q1},t,'q0',{'a'})

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'a'
    
    def test_get_regex_2(self):
        q0 = State('q0','q0')
        q1 = State('q1','q1',True)
        q2 = State('q2','q2',True)

        t = Table()

        t['q0','a'] = 'q1'
        t['q0','b'] = 'q2'

        aut = create_dfa({q0,q1,q2},t,'q0',{'a','b'})

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'a|b' or regex == 'b|a' or regex == '(a|b)' or regex == '(b|a)'
    
    def test_get_regex_3(self):
        q0 = State('q0','q0')
        q1 = State('q1','q1')
        q2 = State('q2','q2',True)

        t = Table()

        t['q0','a'] = 'q1'
        t['q1','b'] = 'q2'

        aut = create_dfa({q0,q1,q2},t,'q0',{'a','b'})

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'ab'
    
    def test_get_regex_4(self):
        q0 = State('q0','q0',True)

        t = Table()

        t['q0','a'] = 'q0'

        aut = create_dfa({q0},t,'q0',{'a'})

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'a*'

    def test_get_regex_5(self):
        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        t = Table()

        t['q0','a'] = 'q1'
        t['q1','a'] = 'q1'

        aut = create_dfa({q0,q1},t,'q0',{'a'})

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'aa*'

    def test_get_regex_6(self):
        aut = DFA('q0','q0',{'a'},True)
        regex = RegexEngine.GetRegex(aut)
        assert regex == ''
    
    def test_get_regex_for_empty_automaton_1(self):
        aut = DFA('q0','q0',{'a'})
        with pytest.raises(ValueError,match='Automaton must have at least one final state'):
            regex = RegexEngine.GetRegex(aut)
    
    def test_get_regex_for_empty_automaton_2(self):
        q0 = State('q0','q0')
        q1 = State('q1','q1',True)

        t = Table()

        t['q0','a'] = 'q0'

        aut = create_dfa({q0,q1},t,'q0',{'a'})
        with pytest.raises(ValueError,match='unreachables states detected'):
            regex = RegexEngine.GetRegex(aut)
    
    def test_get_regex_from_nfa_1(self):

        aut = NFA('q0','q0',{'a'})
        q0 = aut.start_state
        q1 = State('q1','q1')
        q2 = State('q2','q2',True)

        aut.add_epsilon_transition(q0,q1)
        aut += q1,'a',q2

        regex = RegexEngine.GetRegex(aut)

        assert regex == 'a'

    def test_get_regex_from_nfa_2(self):

        aut = NFA('q0','q0',{'a'})
        q0 = aut.start_state
        q1 = State('q1','q1')
        q2 = State('q2','q2',True)

        aut.add_epsilon_transition(q1,q2)
        aut += q0,'a',q1

        regex = RegexEngine.GetRegex(aut)

        assert regex == 'a'
    
    def test_get_regex_from_nfa_3(self):

        aut = NFA('q0','q0',{'a','b'})
        q0 = aut.start_state
        q1 = State('q1','q1',True)
        q2 = State('q2','q2')

        aut += q0,'b',q1
        aut += q1,'a',q2

        aut.add_epsilon_transition(q2,q0)

        regex = RegexEngine.GetRegex(aut)

        assert regex == '(ba)*b'
    
    def test_get_regex_from_nfa_4(self):

        aut = NFA('q0','q0',{'a','b'})
        q0 = aut.start_state
        q1 = State('q1','q1',True)

        aut.add_epsilon_transition(q0,q1)

        regex = RegexEngine.GetRegex(aut)

        assert regex == ''
    
    def test_get_regex_with_epsilon_accept_1(self):
        aut = NFA('q0','q0',{'a'})
        q0 = aut.start_state
        q1 = State('q1','q1',True)

        aut += q0,'a',q1
        aut.add_epsilon_transition(q0,q1)

        regex = RegexEngine.GetRegex(aut)
        assert regex == 'a?'
    
    def test_get_regex_with_epsilon_accept_2(self):
        aut = NFA('q0','q0',{'a','b'})
        q0 = aut.start_state
        q1 = State('q1','q1')
        q2 = State('q2','q2',True)

        aut += q0,'a',q1
        aut += q1,'b',q2
        aut.add_epsilon_transition(q0,q2)

        regex = RegexEngine.GetRegex(aut)
        assert regex == '(ab)?'
    
    def test_get_regex_with_epsilon_accept_3(self):
        aut = NFA('q0','q0',{'a','b'})
        q0 = aut.start_state
        q1 = State('q1','q1')
        q2 = State('q2','q2')
        q3 = State('q3','q3')
        q4 = State('q4','q4')
        q5 = State('q5','q5',True)

        aut += q0,'a',q1
        aut += q1,'b',q2
        aut += q2,'a',q3
        aut.add_epsilon_transition(q0,q3)
        aut += q3,'b',q4
        aut += q4,'a',q5
        aut.add_epsilon_transition(q3,q5)

        regex = RegexEngine.GetRegex(aut)
        assert regex in ['((ba)?|aba(ba)?)','(ba)?|aba(ba)?','(aba(ba)?|(ba)?)','aba(ba)?|(ba)?','(aba)?(ba)?']
    
    def test_get_regex_5_mul_binary(self):
        start = State('start','start')
        q0 = State('q0',0,True)
        q1 = State('q1',1)
        q2 = State('q2',2)
        q3 = State('q3',3)
        q4 = State('q4',4)

        t = Table()

        t['start','0'] = 'q0'
        t['start','1'] = 'q1'

        t['q0','0'] = 'q0'
        t['q0','1'] = 'q1'

        t['q1','0'] = 'q2'
        t['q1','1'] = 'q3'

        t['q2','0'] = 'q4'
        t['q2','1'] = 'q0'

        t['q3','0'] = 'q1'
        t['q3','1'] = 'q2'

        t['q4','0'] = 'q3'
        t['q4','1'] = 'q4'

        aut = create_dfa({start,q0,q1,q2,q3,q4},t,'start',{'0','1'})

        regex = RegexEngine.GetRegex(aut)

        aut_re = RegexEngine.Parse(regex)

        for _ in range(100):
            k = random.randint(1,6)
            word = random.choices(['0','1'],k=k)
            assert aut_re.accept(word) == (int(''.join(word),2) % 5 == 0)
    
    def test_get_regex_3_mul_decimal(self):
        start = State('start','start')
        q0 = State('q0',0,True)
        q1 = State('q1',1)
        q2 = State('q2',2)

        t = Table()

        for i in range(10):
            t['start',str(i)] = f'q{i%3}'
            t['q0',str(i)] = f'q{i%3}'

            for j in range(1,3):
                t[f'q{j}',str(i)] = f'q{(i+j)%3}'
        
        aut = create_dfa({q0,q1,q2,start},t,'start',set(string.digits))

        regex = RegexEngine.GetRegex(aut)

        aut_re = RegexEngine.Parse(regex)
        
        for _ in range(1000):
            k = random.randint(1,3)
            word = random.choices(string.digits,k=k)
            assert aut_re.accept(word) == (int(''.join(word)) % 3 == 0)