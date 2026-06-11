import pytest
import string
import random
import re
from regex.engine import RegexEngine

class TestIntegrationRegex:

    def test_parse_simples_re(self):
        aut = RegexEngine.parse('a')
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
        aut = RegexEngine.parse(re_exp)
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
        aut = RegexEngine.parse(re_exp)
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
        aut = RegexEngine.parse(re_exp)
        for _ in range(1000):
            k = random.randint(0,10)
            word = random.choices(string.printable,k=k)
            assert aut.accept(word) == (re.fullmatch(re_exp,''.join(word)) is not None)
    
    def test_parse_regex_3(self):
        aut = RegexEngine.parse('(hello)*')
        assert aut.accept(list('hello'))
        assert aut.accept(list(''))
        assert aut.accept(list('hellohellohellohellohello'))
        assert not aut.accept(list('hell'))
        assert not aut.accept(list('h'))
        assert not aut.accept(list('hellohe'))
        assert not aut.accept(list('hellohellohel'))
        aut = RegexEngine.parse('(hello)+')
        assert aut.accept(list('hello'))
        assert aut.accept(list('hellohellohellohellohello'))
        assert not aut.accept(list(''))
        assert not aut.accept(list('hell'))
        assert not aut.accept(list('h'))
        assert not aut.accept(list('hellohe'))
        assert not aut.accept(list('hellohellohel'))
        aut = RegexEngine.parse('(hello)?')
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
        aut = RegexEngine.parse(re_exp)
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
        aut = RegexEngine.parse(re_exp)
        assert aut.accept(list(word)) == should_accept
    
    def test_parser_regex_6(self):
        aut = RegexEngine.parse('.')
        for char in string.printable:
            assert aut.accept([char]) == (char != '\n')
    
    def test_parser_regex_7(self):
        aut = RegexEngine.parse('.*')
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
        aut = RegexEngine.parse(re_exp)
        assert aut.accept(list(text)) == should_accept