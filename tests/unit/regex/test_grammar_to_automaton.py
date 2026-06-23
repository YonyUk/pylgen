import pytest

from pylgen.regex import RegexEngine
from pylgen.grammar import Grammar
from pylgen.common.types import Symbol

class TestGrammarToAutomaton:

    @pytest.fixture
    def G1(self) -> Grammar:
        '''
        S -> a S | b S | ε

        L(G) = {a,b}*
        '''
        S = Symbol('S')
        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += a,S
        G[S] += b,S
        G[S] += eps,

        return G
    
    @pytest.fixture
    def G2(self) -> Grammar:
        '''
        S → S a | S b | ε

        L(G) = {a,b}*
        '''
        S = Symbol('S')
        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += S,a
        G[S] += S,b
        G[S] += eps,

        return G
    
    @pytest.fixture
    def G3(self) -> Grammar:
        '''
        S -> ε

        L(G) = { ε }
        '''

        S = Symbol('S')
        eps = Symbol('ε',True,True)

        G = Grammar(S)
        
        G[S] += eps,

        return G

    @pytest.fixture
    def G4(self) -> Grammar:
        '''
        S -> a S

        L(G) = ∅
        '''

        S = Symbol('S')
        a = Symbol('a',True)

        G = Grammar(S)

        G[S] += a,S

        return G

    @pytest.fixture
    def G5(self) -> Grammar:
        '''
        S -> S a

        L(G) = ∅
        '''

        S = Symbol('S')
        a = Symbol('a',True)

        G = Grammar(S)

        G[S] += S,a

        return G

    @pytest.fixture
    def G6(self) -> Grammar:
        '''
        S -> a A

        A -> b A | c

        L(G) = ab*c
        '''

        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += a,A

        G[A] += b,A
        G[A] += c,

        return G
    
    @pytest.fixture
    def G7(self) -> Grammar:
        '''
        S -> A c

        A -> A b | a

        L(G) = ab*c
        '''

        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += A,c
        
        G[A] += A,b
        G[A] += a,

        return G
    
    @pytest.fixture
    def G8(self) -> Grammar:
        '''
        S -> a S | b

        L(G) = a*b
        '''

        S = Symbol('S')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += a,S
        G[S] += b,

        return G
    
    @pytest.fixture
    def G9(self) -> Grammar:
        '''
        S -> A b

        A -> A a | ε

        L(G) = a*b
        '''

        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += A,b

        G[A] += A,a
        G[A] += eps,

        return G
    
    @pytest.fixture
    def G10(self) -> Grammar:
        '''
        S -> a A | b A | ε

        A -> a S | b S

        L(G) = { w ∈ {a,b}* | |w| ≡ 0 mod 2 }
        '''

        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += a,A
        G[S] += b,A
        G[S] += eps,

        G[A] += a,S
        G[A] += b,S

        return G
    
    @pytest.fixture
    def G11(self) -> Grammar:
        '''
        S → A a | A b | ε
        
        A → S a | S b

        L(G) = { w ∈ {a,b}* | |w| ≡ 0 mod 2 }
        '''
        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += A,a
        G[S] += A,b
        G[S] += eps,

        G[A] += S,a
        G[A] += S,b

        return G
    
    @pytest.fixture
    def G12(self) -> Grammar:
        '''
        S → a A | b B
        
        A → a A | b
        
        B → b B | a

        L(G) = { aⁿb | n≥1 } U { bᵐa | m≥1 }
        '''

        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += a,A
        G[S] += b,B

        G[A] += a,A
        G[A] += b,

        G[B] += b,B
        G[B] += a,

        return G
    
    @pytest.fixture
    def G13(self) -> Grammar:
        '''
        S → A b | B a
        
        A → A a | a
        
        B → B b | b
        
        L(G) = { aⁿb | n≥1 } U { bᵐa | m≥1 }
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += A,b
        G[S] += B,a

        G[A] += A,a
        G[A] += a,

        G[B] += B,b
        G[B] += b,

        return G
    
    @pytest.fixture
    def G14(self) -> Grammar:
        '''
        S → a A | ε
        
        A → b B
        
        B → a S

        L(G) = (aba)*
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += a,A
        G[S] += eps,

        G[A] += b,B

        G[B] += a,S

        return G
    
    @pytest.fixture
    def G15(self) -> Grammar:
        '''
        S -> A a | ε

        A -> B b

        B -> S a

        L(G = (aba)*
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += A,a
        G[S] += eps,

        G[A] += B,b

        G[B] += S,a

        return G
    
    @pytest.fixture
    def G16(self) -> Grammar:
        '''
        S → a S | b
        
        C → c C
        
        L(G) = a*b
        '''
        S = Symbol('S')
        C = Symbol('C')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += a,S
        G[S] += b,

        G[C] += c,C

        return G
    
    @pytest.fixture
    def G17(self) -> Grammar:
        '''
        S → S a | b
        
        C → C c
        
        L(G) = ba*
        '''
        S = Symbol('S')
        C = Symbol('C')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += S,a
        G[S] += b,

        G[C] += C,c

        return G
    
    @pytest.fixture
    def G18(self) -> Grammar:
        '''
        S → a A
        
        A → b A | c
        
        B → d B

        L(G) = ab*c
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        d = Symbol('d',True)

        G = Grammar(S)

        G[S] += a,A

        G[A] += b,A
        G[A] += c,

        G[B] += d,B

        return G
    
    @pytest.fixture
    def G19(self) -> Grammar:
        '''
        S → A c
        
        A → A b | a
        
        B → B d

        L(G) = ab*c
        '''

        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        d = Symbol('d',True)

        G = Grammar(S)

        G[S] += A,c

        G[A] += A,b
        G[A] += a,

        G[B] += B,d

        return G
    
    @pytest.fixture
    def G20(self) -> Grammar:
        '''
        S -> a A

        A -> B
        
        B -> b B | c

        L(G) = ab*c
        '''

        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += a,A

        G[A] += B,

        G[B] += b,B
        G[B] += c,

        return G

    @pytest.fixture
    def G21(self) -> Grammar:
        '''
        S -> B c

        B -> A
        
        A -> A b | a

        L(G) = ab*c
        '''

        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)

        G = Grammar(S)

        G[S] += B,c

        G[B] += A,

        G[A] += A,b
        G[A] += a,

        return G
    
    @pytest.fixture
    def G22(self) -> Grammar:
        '''
        S -> A

        A -> B

        B -> a S | b

        L(G) = a*b
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += A,

        G[A] += B,

        G[B] += a,S
        G[B] += b,

        return G

    @pytest.fixture
    def G23(self) -> Grammar:
        '''
        S -> B b

        B -> A

        A -> A a | ε

        L(G) = a*b
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += B,b

        G[B] += A,

        G[A] += A,a
        G[A] += eps,

        return G
    
    @pytest.fixture
    def G24(self) -> Grammar:
        '''
        S -> a A | ε

        A -> B

        B -> b S

        L(G) = (ab)*
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += a,A
        G[S] += eps,

        G[A] += B,

        G[B] += b,S

        return G

    @pytest.fixture
    def G25(self) -> Grammar:
        '''
        S -> B b | ε

        B -> A

        A -> S a

        L(G) = (ab)*
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        eps = Symbol('ε',True,True)

        G = Grammar(S)

        G[S] += B,b
        G[S] += eps,

        G[B] += A,

        G[A] += S,a

        return G
    
    @pytest.fixture
    def G26(self) -> Grammar:
        '''
        S -> A

        A -> S

        L(G) = ∅
        '''
        S = Symbol('S')
        A = Symbol('A')

        G = Grammar(S)

        G[S] += A,
        G[A] += S,

        return G
    
    @pytest.fixture
    def G27(self) -> Grammar:
        '''
        S -> a S | A

        A -> B

        B -> b

        L(G) = a*b
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += a,S
        G[S] += A,

        G[A] += B,

        G[B] += b,

        return G
    
    @pytest.fixture
    def G28(self) -> Grammar:
        '''
        S -> S a | A

        A -> B

        B -> b
        
        L(G) = ba*
        '''
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = Grammar(S)

        G[S] += S,a
        G[S] += A,

        G[A] += B,

        G[B] += b,

        return G
    
    @pytest.fixture
    def G29(self) -> Grammar:
        '''
        S -> 0 S | 1 A

        A -> 0 S | 1 A | ε
        '''
        S = Symbol('S')
        A = Symbol('A')

        _0 = Symbol('0',True)
        _1 = Symbol('1',True)
        eps = Symbol('epsilon',True,True)

        G = Grammar(S)

        G[S] += _0,S
        G[S] += _1,A

        G[A] += _0,S
        G[A] += _1,A
        G[A] += eps,
    
        return G
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',True),
        ('a',True),
        ('aabababbabbab',True),
        ('bababbababbabaa',True),
        ('aaaaaaaaaaaaaa',True),
        ('bbbbbbbbbbbbbbbb',True),
        ('aaaaaaaaaab',True),
        ('bbbbbbbbbbbbbbbbbba',True),
        ('a0a',False),
        ('b0b',False)
    ])
    def test_grammar_to_automaton_1(self,string:str,should_accept:bool,G1:Grammar):

        aut = RegexEngine.GetAutomaton(G1)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',True),
        ('a',True),
        ('aabababbabbab',True),
        ('bababbababbabaa',True),
        ('aaaaaaaaaaaaaa',True),
        ('bbbbbbbbbbbbbbbb',True),
        ('aaaaaaaaaab',True),
        ('bbbbbbbbbbbbbbbbbba',True),
        ('a0a',False),
        ('b0b',False)
    ])
    def test_grammar_to_automaton_2(self,string:str,should_accept:bool,G2:Grammar):

        aut = RegexEngine.GetAutomaton(G2)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('ababbab',False),
        ('babbab',False),
        ('aaaab',False),
        ('bbbbbba',False)
    ])
    def test_grammar_to_automaton_3(self,string:str,should_accept:bool,G3:Grammar):

        aut = RegexEngine.GetAutomaton(G3)

        assert aut.accept(list(string)) == should_accept

    def test_grammar_to_automaton_4(self,G4:Grammar):

        aut = RegexEngine.GetAutomaton(G4)

        assert aut.is_empty
    
    def test_grammar_to_automaton_5(self,G5:Grammar):
        
        aut = RegexEngine.GetAutomaton(G5)

        assert aut.is_empty
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('c',False),
        ('b',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abbbbbbc',True),
        ('abc',True)
    ])
    def test_grammar_to_automaton_6(self,string:str,should_accept:bool,G6:Grammar):
        
        aut = RegexEngine.GetAutomaton(G6)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('c',False),
        ('b',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abbbbbbc',True),
        ('abc',True)
    ])
    def test_grammar_to_automaton_7(self,string:str,should_accept:bool,G7:Grammar):
        
        aut = RegexEngine.GetAutomaton(G7)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('ab',True),
        ('aaaaab',True),
        ('aab',True)
    ])
    def test_grammar_to_automaton_8(self,string:str,should_accept:bool,G8:Grammar):
        
        aut = RegexEngine.GetAutomaton(G8)

        assert aut.accept(list(string)) == should_accept

    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('ab',True),
        ('aaaaab',True),
        ('aab',True)
    ])
    def test_grammar_to_automaton_9(self,string:str,should_accept:bool,G9:Grammar):
        
        aut = RegexEngine.GetAutomaton(G9)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('aa',True),
        ('bb',True),
        ('ab',True),
        ('aaa',False),
        ('aab',False),
        ('aba',False),
        ('baa',False),
        ('abb',False),
        ('bab',False),
        ('bba',False),
        ('bbb',False),
        ('aaaa',True),
        ('aaab',True),
        ('aaba',True),
        ('abaa',True),
        ('baaa',True),
        ('aabb',True),
        ('abab',True),
        ('baab',True),
        ('abba',True),
        ('baba',True),
        ('bbaa',True),
        ('abbb',True),
        ('babb',True),
        ('bbab',True),
        ('bbba',True),
        ('bbbb',True)
    ])
    def test_grammar_to_automaton_10(self,string:str,should_accept:bool,G10:Grammar):

        aut = RegexEngine.GetAutomaton(G10)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('aa',True),
        ('bb',True),
        ('ab',True),
        ('aaa',False),
        ('aab',False),
        ('aba',False),
        ('baa',False),
        ('abb',False),
        ('bab',False),
        ('bba',False),
        ('bbb',False),
        ('aaaa',True),
        ('aaab',True),
        ('aaba',True),
        ('abaa',True),
        ('baaa',True),
        ('aabb',True),
        ('abab',True),
        ('baab',True),
        ('abba',True),
        ('baba',True),
        ('bbaa',True),
        ('abbb',True),
        ('babb',True),
        ('bbab',True),
        ('bbba',True),
        ('bbbb',True)
    ])
    def test_grammar_to_automaton_11(self,string:str,should_accept:bool,G11:Grammar):

        aut = RegexEngine.GetAutomaton(G11)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',False),
        ('ab',True),
        ('aba',False),
        ('aab',True),
        ('baa',False),
        ('bba',True),
        ('bab',False),
        ('aaaaaaab',True),
        ('bbbbbbbbbba',True),
        ('aaaaabbbbb',False),
        ('bbbbbbaaaaaaa',False),
        ('ababababab',False),
        ('aaab',True),
        ('bbbba',True)
    ])
    def test_grammar_to_automaton_12(self,string:str,should_accept:bool,G12:Grammar):
        
        aut = RegexEngine.GetAutomaton(G12)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',False),
        ('ab',True),
        ('aba',False),
        ('aab',True),
        ('baa',False),
        ('bba',True),
        ('bab',False),
        ('aaaaaaab',True),
        ('bbbbbbbbbba',True),
        ('aaaaabbbbb',False),
        ('bbbbbbaaaaaaa',False),
        ('ababababab',False),
        ('aaab',True),
        ('bbbba',True)
    ])
    def test_grammar_to_automaton_13(self,string:str,should_accept:bool,G13:Grammar):
        
        aut = RegexEngine.GetAutomaton(G13)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('ab',False),
        ('aa',False),
        ('ba',False),
        ('bb',False),
        ('aaa',False),
        ('aab',False),
        ('aba',True),
        ('baa',False),
        ('abb',False),
        ('bab',False),
        ('bba',False),
        ('bbb',False),
        ('abaaba',True),
        ('ababa',False),
        ('ababababababa',False),
        ('abaabaabaaba',True)
    ])
    def test_grammar_to_automaton_14(self,string:str,should_accept:bool,G14:Grammar):

        aut = RegexEngine.GetAutomaton(G14)

        assert aut.accept(list(string)) == should_accept

    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('ab',False),
        ('aa',False),
        ('ba',False),
        ('bb',False),
        ('aaa',False),
        ('aab',False),
        ('aba',True),
        ('baa',False),
        ('abb',False),
        ('bab',False),
        ('bba',False),
        ('bbb',False),
        ('abaaba',True),
        ('ababa',False),
        ('ababababababa',False),
        ('abaabaabaaba',True)
    ])
    def test_grammar_to_automaton_15(self,string:str,should_accept:bool,G15:Grammar):

        aut = RegexEngine.GetAutomaton(G15)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('aa',False),
        ('ab',True),
        ('ba',False),
        ('bb',False),
        ('c',False),
        ('abc',False),
        ('aaaaaac',False),
        ('aaaaaabc',False),
        ('aaaaaab',True)
    ])
    def test_grammar_to_automaton_16(self,string:str,should_accept:bool,G16:Grammar):

        aut = RegexEngine.GetAutomaton(G16)

        assert aut.accept(list(string)) == should_accept

    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('aa',False),
        ('ab',False),
        ('ba',True),
        ('bb',False),
        ('bac',False),
        ('bc',False),
        ('baaaaa',True),
        ('baaaac',False)
    ])
    def test_grammar_to_automaton_17(self,string:str,should_accept:bool,G17:Grammar):

        aut = RegexEngine.GetAutomaton(G17)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',False),
        ('c',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abc',True),
        ('adc',False),
        ('abbbbbbc',True),
        ('abbbbbbdc',False)
    ])
    def test_grammar_to_automaton_18(self,string:str,should_accept:bool,G18:Grammar):

        aut = RegexEngine.GetAutomaton(G18)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',False),
        ('c',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abc',True),
        ('adc',False),
        ('abbbbbbc',True),
        ('abbbbbbdc',False)
    ])
    def test_grammar_to_automaton_19(self,string:str,should_accept:bool,G19:Grammar):

        aut = RegexEngine.GetAutomaton(G19)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('c',False),
        ('b',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abbbbbbc',True),
        ('abc',True)
    ])
    def test_grammar_to_automaton_20(self,string:str,should_accept:bool,G20:Grammar):
        
        aut = RegexEngine.GetAutomaton(G20)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('c',False),
        ('b',False),
        ('ab',False),
        ('ac',True),
        ('bc',False),
        ('abbbbbbc',True),
        ('abc',True)
    ])
    def test_grammar_to_automaton_21(self,string:str,should_accept:bool,G21:Grammar):
        
        aut = RegexEngine.GetAutomaton(G21)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('ab',True),
        ('aaaaab',True),
        ('aab',True)
    ])
    def test_grammar_to_automaton_22(self,string:str,should_accept:bool,G22:Grammar):

        aut = RegexEngine.GetAutomaton(G22)

        assert aut.accept(list(string)) == should_accept

    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('ab',True),
        ('aaaaab',True),
        ('aab',True)
    ])
    def test_grammar_to_automaton_23(self,string:str,should_accept:bool,G23:Grammar):

        aut = RegexEngine.GetAutomaton(G23)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('aa',False),
        ('ab',True),
        ('ba',False),
        ('bb',False),
        ('aba',False),
        ('abab',True),
        ('ababababababab',True),
        ('ababababababa',False)
    ])
    def test_grammar_to_automaton_24(self,string:str,should_accept:bool,G24:Grammar):

        aut = RegexEngine.GetAutomaton(G24)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',True),
        ('a',False),
        ('b',False),
        ('aa',False),
        ('ab',True),
        ('ba',False),
        ('bb',False),
        ('aba',False),
        ('abab',True),
        ('ababababababab',True),
        ('ababababababa',False)
    ])
    def test_grammar_to_automaton_25(self,string:str,should_accept:bool,G25:Grammar):

        aut = RegexEngine.GetAutomaton(G25)

        assert aut.accept(list(string)) == should_accept
    
    def test_grammar_to_automaton_26(self,G26:Grammar):

        aut = RegexEngine.GetAutomaton(G26)

        assert aut.is_empty
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('aa',False),
        ('ab',True),
        ('ba',False),
        ('bb',False),
        ('aaaaaab',True)
    ])
    def test_grammar_to_automaton_27(self,string:str,should_accept:bool,G27:Grammar):

        aut = RegexEngine.GetAutomaton(G27)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('a',False),
        ('b',True),
        ('aa',False),
        ('ab',False),
        ('ba',True),
        ('bb',False),
        ('baaaaa',True),
    ])
    def test_grammar_to_automaton_28(self,string:str,should_accept:bool,G28:Grammar):

        aut = RegexEngine.GetAutomaton(G28)

        assert aut.accept(list(string)) == should_accept
    
    @pytest.mark.parametrize("string,should_accept",[
        ('',False),
        ('0',False),
        ('1',True),
        ('01',True),
        ('010',False),
        ('0010101001001',True),
        ('0100101010010',False),
        ('0000001',True),
        ('011111111',True),
        ('0001111111110',False)
    ])
    def test_grammar_to_automaton_29(self,string:str,should_accept:bool,G29:Grammar):

        aut = RegexEngine.GetAutomaton(G29)
        assert aut.accept(list(string)) == should_accept