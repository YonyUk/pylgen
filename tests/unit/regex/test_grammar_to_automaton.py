import pytest

from regex import RegexEngine
from grammar import Grammar
from common.types import Symbol

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
        
        A → a A | a
        
        B → b B | b
        
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

        G[A] += a,A
        G[A] += a,

        G[B] += b,B
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
        S -> 

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