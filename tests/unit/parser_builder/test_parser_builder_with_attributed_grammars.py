from typing import Dict, List, Tuple
from datetime import datetime
from random import choice, randint, random

import pytest
import time
from pylgen.common.types import AST, Symbol,ASTListView
from pylgen.grammar.grammar import Grammar,AttributedGrammar,Production
from pylgen.parser.parser_builder import LALRReduceReduceConflictException, LALRShiftReduceConflictException, ParserBuilder
from pylgen.parser.bottom_up_parser_actions import BottomUpParserAction
from pylgen.parser.lr0_parser import LR0Item,LR0State
from pylgen.parser.lalr_parser import LALRItem,LALRState

def comodin_reductor(asts:ASTListView) -> AST:
    return AST(Symbol('s'),0,0)

class TestParserBuilderWithAttributedGrammars:

    @pytest.fixture
    def classic_lalr_1_grammar(self) -> Tuple[AttributedGrammar,Tuple[Symbol,...]]:
        S = Symbol('S')
        L = Symbol('L')
        R = Symbol('R')

        mul = Symbol('*',True)
        id_ = Symbol('id',True)
        eq = Symbol('=',True)

        G = AttributedGrammar(S,'$')

        G[S] += (L,eq,R),comodin_reductor
        G[S] += (R,),comodin_reductor

        G[L] += (mul,R),comodin_reductor
        G[L] += (id_,),comodin_reductor

        G[R] += (L,),comodin_reductor

        return G,(S,L,R,mul,id_,eq,G.end_symbol)
    
    @pytest.fixture
    def conflict_reduce_reduce_lalr_1_grammar_1(self) -> Tuple[AttributedGrammar,Tuple[Symbol,...]]:
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        d = Symbol('d',True)
        e = Symbol('e',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,A,d),comodin_reductor
        G[S] += (b,B,d),comodin_reductor
        G[S] += (a,B,e),comodin_reductor
        G[S] += (b,A,e),comodin_reductor

        G[A] += (c,),comodin_reductor
        G[B] += (c,),comodin_reductor

        return G,(S,A,B,a,b,c,d,e,G.end_symbol)
    
    @pytest.fixture
    def arithmetic_grammar(self) -> Tuple[AttributedGrammar,Tuple[Symbol,...]]:
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')
        P = Symbol('P')

        plus = Symbol('+',True)
        minus = Symbol('-',True)
        mul = Symbol('*',True)
        div = Symbol('/',True)
        exp = Symbol('**',True)
        mod = Symbol('%',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (E,minus,T),comodin_reductor
        G[E] += (E,mod,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (T,mul,F),comodin_reductor
        G[T] += (T,div,F),comodin_reductor
        G[T] += (F,),comodin_reductor

        G[F] += (F,exp,P),comodin_reductor
        G[F] += (P,),comodin_reductor

        G[P] += (lp,E,rp),comodin_reductor
        G[P] += (id_,),comodin_reductor

        return G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,G.end_symbol)
    
    def generate_valid_tokens_string(self,g:Grammar):
        symbol = g.start_symbol
        tokens:List[Symbol] = [symbol]
        while symbol:
            index = tokens.index(symbol)
            options = g[symbol].productions
            red = min(options,key=lambda symbols:len(symbols))
            if random() < .5:
                selected = red
            else:
                selected = choice(options)
            tokens = tokens[:index] + selected + tokens[index+1:]
            symbol = None
            for s in tokens:
                if not s.is_terminal:
                    symbol = s
                    break
        return tokens

    def simulate_parsing(self,tokens:List[Symbol],goto:Dict[Tuple[LALRState,Symbol],LALRState],action:Dict[Tuple[LALRState,Symbol],Tuple[str,LALRState | Production]]) -> bool:
        '''
        simulate the parsing and return True if the sequence of tokens was successfully parsed, False otherwise
        '''
        stack = []
        stack_states = []
        initial_state = list(filter(lambda t:t[0].index == 0,goto.keys()))[0][0]
        while len(stack) > 0 or len(tokens) > 0:
            state = initial_state
            stack_states = [state]
            for symbol in stack:
                if not (state,symbol) in action:
                    break
                act = action[(state,symbol)]
                if act[0] == BottomUpParserAction.SHIFT:
                    state = goto[(state,symbol)]
                    stack_states.append(state)
                elif act[0] == BottomUpParserAction.REDUCE and len(tokens) > 0:
                    break
            if len(tokens) == 0 or not (state,tokens[0]) in action:
                break
            act = action[(state,tokens[0])]
            while act[0] == BottomUpParserAction.REDUCE:
                p:Production = act[1] # type: ignore
                stack = stack[:-1*len(p.production)] + [p.head]
                stack_states = stack_states[:-1*len(p.production)]
                state = stack_states[-1]
                if not (state,stack[-1]) in action:
                    break
                act = action[(state,stack[-1])]
                if act[0] != BottomUpParserAction.SHIFT:
                    break
                state = goto[(state,stack[-1])]
                stack_states.append(state)
                if not (state,tokens[0]) in action:
                    break
                act = action[(state,tokens[0])]
            if act[0] == BottomUpParserAction.SHIFT:
                stack.append(tokens[0])
                stack_states.append(state)
            if act[0] == BottomUpParserAction.ACCEPT:
                return True
            tokens.pop(0)
        return False

    def test_lr0_closure_1(self):
        closure = ParserBuilder.closure_lr0(set(),AttributedGrammar(Symbol('S')))
        assert len(closure) == 0
    
    def test_lr0_closure_2(self):
        A = Symbol('A')
        a = Symbol('a',True)
        b = Symbol('b',True)
        lr0_item = LR0Item(A,[a],[b])
        closure = ParserBuilder.closure_lr0({lr0_item},AttributedGrammar(Symbol('S')))
        assert closure == { lr0_item }
    
    def test_lr0_closure_3(self):
        S = Symbol('S')
        E = Symbol('E')
        id_ = Symbol('id',True)

        G = AttributedGrammar(S,'$')

        G[S] += (E,),comodin_reductor
        G[E] += (id_,),comodin_reductor

        lr0_item = LR0Item(S,[],[E])
        new_item = LR0Item(E,[],[id_])
        closure = ParserBuilder.closure_lr0({lr0_item},G)
        assert closure == { new_item, lr0_item }
    
    def test_lr0_closure_4(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        G = AttributedGrammar(S,'$')

        G[S] += (A,),comodin_reductor
        G[A] += (B,),comodin_reductor
        G[B] += (A,),comodin_reductor

        item1 = LR0Item(A,[],[B])
        item2 = LR0Item(B,[],[A])
        closure = ParserBuilder.closure_lr0({ item1, item2 },G)
        assert closure == { item1, item2 }
    
    def test_lr0_closure_5(self):
        S = Symbol('S')
        A = Symbol('A')
        eps = Symbol('ε',True,True)

        G = AttributedGrammar(S,'$')

        G[S] += (A,),comodin_reductor
        G[A] += (eps,),comodin_reductor

        item = LR0Item(A,[],[eps])
        closure = ParserBuilder.closure_lr0({item},G)
        assert closure == { item }

    def test_lr0_closure_6(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(S,L,R,mul,id_,eq,end_symbol) = classic_lalr_1_grammar

        item1 = LR0Item(Symbol("S'"),[],[S])
        item2 = LR0Item(S,[],[R])
        item3 = LR0Item(S,[],[L,eq,R])
        item4 = LR0Item(L,[],[mul,R])
        item5 = LR0Item(L,[],[id_])
        item6 = LR0Item(R,[],[L])

        closure = ParserBuilder.closure_lr0({item1},G)
        assert closure == {item1,item2,item3,item4,item5,item6}

    def test_lr0_closure_7(self,arithmetic_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,end_symbol) = arithmetic_grammar

        item1 = LR0Item(Symbol("E'"),[],[E])
        item2 = LR0Item(E,[],[E,plus,T])
        item3 = LR0Item(E,[],[E,minus,T])
        item4 = LR0Item(E,[],[E,mod,T])
        item5 = LR0Item(E,[],[T])
        item6 = LR0Item(T,[],[T,mul,F])
        item7 = LR0Item(T,[],[T,div,F])
        item8 = LR0Item(T,[],[F])
        item9 = LR0Item(F,[],[F,exp,P])
        item10 = LR0Item(F,[],[P])
        item11 = LR0Item(P,[],[lp,E,rp])
        item12 = LR0Item(P,[],[id_])

        closure = ParserBuilder.closure_lr0({item1},G)
        assert closure == {item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,item11,item12}

    def test_lr0_closure_cache_1(self):
        S = Symbol('S')
        E = Symbol('E')
        id_ = Symbol('id',True)

        G = AttributedGrammar(S,'$')

        G[S] += (E,),comodin_reductor
        G[E] += (id_,),comodin_reductor

        lr0_item = LR0Item(S,[],[E])
        t = datetime.now()
        closure1 = ParserBuilder.closure_lr0({lr0_item},G)
        t0 = datetime.now() - t
        t = datetime.now()
        closure2 = ParserBuilder.closure_lr0({lr0_item},G)
        t1 = datetime.now() - t
        assert t1 < t0
        assert closure1 == closure2

    def test_lr0_closure_cache_2(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(S,L,R,mul,id_,eq,end_symbol) = classic_lalr_1_grammar

        lr0_item = LR0Item(Symbol("S'"),[],[S])
        t = datetime.now()
        closure1 = ParserBuilder.closure_lr0({lr0_item},G)
        t0 = datetime.now() - t
        t = datetime.now()
        closure2 = ParserBuilder.closure_lr0({lr0_item},G)
        t1 = datetime.now() - t
        assert t1 < t0
        assert closure1 == closure2
    
    def test_lr0_closure_cache_3(self,arithmetic_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,end_symbol) = arithmetic_grammar

        item1 = LR0Item(Symbol("E'"),[],[E])

        t = datetime.now()
        closure1 = ParserBuilder.closure_lr0({item1},G)
        t0 = datetime.now() - t
        t = datetime.now()
        closure2 = ParserBuilder.closure_lr0({item1},G)
        t1 = datetime.now() - t

        assert t1 < t0
        assert closure1 == closure2
    
    def test_lalr1_closure_1(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(S,L,R,mul,id_,eq,end_symbol) = classic_lalr_1_grammar

        item = LALRItem(Symbol("S'"),[],[S])

        closure = ParserBuilder.closure_lalr({item},G)
        for i in closure:
            assert len(i.lookaheads) == 0
    
    def test_lalr1_closure_2(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')
        a = Symbol('a',True)
        b = Symbol('b',True)
        G = AttributedGrammar(S,'$')
        G[S] += (A,B),comodin_reductor
        G[A] += (a,),comodin_reductor
        G[B] += (b,),comodin_reductor

        item = LALRItem(Symbol("S'"),[],[S],{G.end_symbol})

        closure = ParserBuilder.closure_lalr({item},G)
        for i in closure:
            if i.head == A and len(i.left) == 0 and i.right == [a]:
                first = G.first([B,G.end_symbol])
                assert first.issubset(i.lookaheads)
                break
    
    def test_lalr1_closure_3(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')
        a = Symbol('a',True)
        b = Symbol('b',True)
        
        G = AttributedGrammar(S,'$')
        
        G[S] += (A,B),comodin_reductor

        G[A] += (B,a),comodin_reductor

        G[B] += (A,b),comodin_reductor
        G[B] += (b,),comodin_reductor

        item = LALRItem(A,[],[B,a],{a,b})

        closure = ParserBuilder.closure_lalr({item},G)
        
        for i in closure:
            if i.head == B and len(i.left) == 0:
                subset = G.first([a,a]).union(G.first([a,b]))
                assert subset.issubset(i.lookaheads)
    
    def test_lalr1_closure_4(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')
        C = Symbol('C')
        a = Symbol('a',True)
        b = Symbol('b',True)
        
        G = AttributedGrammar(S,'$')
        
        G[S] += (A,B),comodin_reductor

        G[A] += (B,a),comodin_reductor
        G[A] += (B,C),comodin_reductor

        G[B] += (A,b),comodin_reductor
        G[B] += (b,),comodin_reductor

        G[C] += (A,b),comodin_reductor

        item = LALRItem(A,[],[B,C],{a,b})

        closure = ParserBuilder.closure_lalr({item},G)
        
        for i in closure:
            if i.head == B and len(i.left) == 0:
                subset = G.first([C,a]).union(G.first([C,b]))
                assert subset.issubset(i.lookaheads)
    
    def test_lalr1_closure_5(self):
        E = Symbol('E')
        T = Symbol('T')
        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[E] += (id_,),comodin_reductor

        item = LALRItem(T,[id_],[],{plus,G.end_symbol})

        closure = ParserBuilder.closure_lalr({item},G)
        assert closure == { item }
    
    def test_lalr1_closure_6(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        plus = Symbol('+',True)

        G = AttributedGrammar(S,'$')

        G[S] += (A,B),comodin_reductor
        G[A] += (a,),comodin_reductor
        G[B] += (b,),comodin_reductor
        G[S] += (plus,),comodin_reductor

        item1 = LALRItem(S,[A],[B],{G.end_symbol})
        item2 = LALRItem(S,[A],[B],{plus})

        closure = ParserBuilder.closure_lalr({item1,item2},G)

        for it in closure:
            if it.head == B and len(it.left) == 0 and it.right == [b]:
                assert it.lookaheads == {G.end_symbol, plus}
    
    def test_lalr1_closure_cache_2(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(S,L,R,mul,id_,eq,end_symbol) = classic_lalr_1_grammar

        lalr_item = LALRItem(Symbol("S'"),[],[S],{end_symbol})
        t = datetime.now()
        closure1 = ParserBuilder.closure_lr0({lalr_item},G)
        t0 = datetime.now() - t
        t = datetime.now()
        closure2 = ParserBuilder.closure_lr0({lalr_item},G)
        t1 = datetime.now() - t
        assert t1 < t0
        assert closure1 == closure2
    
    def test_lalr1_closure_cache_3(self,arithmetic_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,end_symbol) = arithmetic_grammar

        item1 = LALRItem(Symbol("E'"),[],[E],{end_symbol})

        t = datetime.now()
        closure1 = ParserBuilder.closure_lr0({item1},G)
        t0 = datetime.now() - t
        t = datetime.now()
        closure2 = ParserBuilder.closure_lr0({item1},G)
        t1 = datetime.now() - t

        assert t1 < t0
        assert closure1 == closure2
   
    def test_lr0_goto_1(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LALRItem(T,[id_],[])

        goto = ParserBuilder.goto_lr0({item},plus,G)
        assert len(goto) == 0
    
    def test_lr0_goto_2(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LR0Item(T,[],[id_])
        goto = ParserBuilder.goto_lr0({item},id_,G)

        expected = { LR0Item(T,[id_],[]) }

        assert goto == expected
    
    def test_lr0_goto_3(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LR0Item(Symbol("E'"),[],[E])
        goto = ParserBuilder.goto_lr0({item},E,G)

        expected = { LR0Item(Symbol("E'"),[E],[]) }

        assert goto == expected
    
    def test_lalr_goto_1(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LALRItem(T,[id_],[],{ plus,G.end_symbol })
        goto = ParserBuilder.goto_lalr({item},Symbol('*',True),G)
        assert len(goto) == 0
    
    def test_lalr_goto_2(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LALRItem(T,[],[id_],{ plus, G.end_symbol })
        goto = ParserBuilder.goto_lalr({item},id_,G)

        expected = LALRItem(T,[id_],[],{plus,G.end_symbol})
        assert goto == { expected }
    
    def test_lalr_goto_3(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        item = LALRItem(Symbol("E'"),[],[E],{G.end_symbol})
        goto = ParserBuilder.goto_lalr({item},E,G)

        expected = LALRItem(Symbol("E'"),[E],[],{G.end_symbol})

        assert goto == { expected }
    
    def test_lalr_goto_4(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        plus = Symbol('+',True)

        G = AttributedGrammar(S,'$')

        G[S] += (A,B),comodin_reductor
        G[A] += (a,),comodin_reductor
        G[B] += (b,),comodin_reductor
        G[S] += (plus,),comodin_reductor

        item = LALRItem(S,[],[A,B],{plus,G.end_symbol})
        goto = ParserBuilder.goto_lalr({item},A,G)

        assert len(goto) == 2
        for it in goto:
            if it.head == S:
                assert it.left == [A] and it.right == [B] and it.lookaheads == {plus,G.end_symbol}
            elif it.head == B:
                assert len(it.left) == 0 and it.right == [b] and it.lookaheads == {plus,G.end_symbol}
    
    def test_get_canonical_lr0_states_1(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')
        G_ = Grammar.AugmentGrammar(G)

        G[S] += (a,),comodin_reductor

        states = ParserBuilder.get_canonical_lr0_states(G)

        assert len(states) == 3

        i0 = LR0State({
            LR0Item(G_.start_symbol,[],[S]),
            LR0Item(S,[],[a])
        })

        i1 = LR0State({
            LR0Item(G_.start_symbol,[S],[])
        })

        i2 = LR0State({
            LR0Item(S,[a],[])
        })

        assert states == { i0,i1,i2 }
    
    def test_get_canonical_lr0_states_2(self):
        E = Symbol('E')
        T = Symbol('T')
        id_ = Symbol('id',True)
        plus = Symbol('+',True)

        G = AttributedGrammar(E,'$')
        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor
        
        G_ = Grammar.AugmentGrammar(G)

        states = ParserBuilder.get_canonical_lr0_states(G)

        i0 = LR0State({
            LR0Item(Symbol("E'"),[],[E]),
            LR0Item(E,[],[E,plus,T]),
            LR0Item(E,[],[T]),
            LR0Item(T,[],[id_])
        })

        i1 = LR0State({
            LR0Item(Symbol("E'"),[E],[]),
            LR0Item(E,[E],[plus,T])
        })

        i2 = LR0State({
            LR0Item(E,[T],[])
        })

        i3 = LR0State({
            LR0Item(T,[id_],[])
        })

        i4 = LR0State({
            LR0Item(E,[E,plus],[T]),
            LR0Item(T,[],[id_])
        })

        i5 = LR0State({
            LR0Item(E,[E,plus,T],[])
        })

        assert states == { i0,i1,i2,i3,i4,i5 }
    
    def test_get_canonical_lr0_states_3(self):
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)

        G = AttributedGrammar(S,'$')

        G[S] += (A,b),comodin_reductor
        G[A] += (a,),comodin_reductor

        states = ParserBuilder.get_canonical_lr0_states(G)
        for state in states:
            for item in state.items:
                assert B != item.head and B not in item.left and not B in item.right
    
    def test_get_kernel_items_lr0(self):
        E = Symbol('E')
        T = Symbol('T')
        id_ = Symbol('id',True)
        plus = Symbol('+',True)

        G = AttributedGrammar(E,'$')
        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor
        
        G_ = Grammar.AugmentGrammar(G)

        states = ParserBuilder.get_canonical_lr0_states(G)

        i0_kernel = {
            LR0Item(Symbol("E'"),[],[E])
        }

        i1_kernel = {
            LR0Item(Symbol("E'"),[E],[]),
            LR0Item(E,[E],[plus,T])
        }

        i2_kernel = {
            LR0Item(E,[T],[])
        }

        i3_kernel = {
            LR0Item(T,[id_],[])
        }

        i4_kernel = {
            LR0Item(E,[E,plus],[T])
        }

        i5_kernel = {
            LR0Item(E,[E,plus,T],[])
        }

        kernels = [ ParserBuilder.get_kernel_items_lr0(state,G) for state in states ]

        assert i0_kernel in kernels
        assert i1_kernel in kernels
        assert i2_kernel in kernels
        assert i3_kernel in kernels
        assert i4_kernel in kernels
        assert i5_kernel in kernels
    
    def test_get_canonical_lalr_states_1(self):
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')

        plus = Symbol('+',True)
        mul = Symbol('*',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (T,mul,F),comodin_reductor
        G[T] += (F,),comodin_reductor

        G[F] += (lp,E,rp),comodin_reductor
        G[F] += (id_,),comodin_reductor

        states = ParserBuilder.get_canonical_lalr_states(G)

        initial_item = list(filter(lambda state:state.index==0,states))[0]

        found_e_t = False
        found_t_t = False

        for state in states:
            for item in state.items:
                if item.head == E and item.left == [T] and len(item.right) == 0:
                    if item.lookaheads == {plus,rp,G.end_symbol}:
                        found_e_t = True
                elif item.head == T and item.left == [T] and item.right == [mul,F]:
                    if item.lookaheads == { mul,plus,rp,G.end_symbol}:
                        found_t_t = True
        
        assert found_t_t and found_e_t
        for item in initial_item.items:
            if item.head not in G.non_terminals and len(item.left) == 0 and item.right == [E]:
                assert item.lookaheads == { G.end_symbol }
                break
    
    def test_get_canonical_lalr_states_2(self):
        S = Symbol('S')
        A = Symbol('A')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        d = Symbol('d',True)
        e = Symbol('e',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,A,d),comodin_reductor
        G[S] += (b,A,e),comodin_reductor

        G[A] += (c,),comodin_reductor

        states = ParserBuilder.get_canonical_lalr_states(G)
        for state in states:
            kernel = ParserBuilder.get_kernel_items_lalr(state,G)
            if len(kernel) == 1:
                item = next(iter(kernel))
                if item.head == A and len(item.right) == 0 and item.left == [c]:
                    assert item.lookaheads == { e,d }
                    break
    
    def test_get_kernel_items_lalr(self):
        E = Symbol('E')
        T = Symbol('T')
        
        plus = Symbol('+',True)
        mul = Symbol('*',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (T,mul,id_),comodin_reductor
        G[T] += (id_,),comodin_reductor

        states = ParserBuilder.get_canonical_lalr_states(G)

        target = None
        for state in states:
            kernels = ParserBuilder.get_kernel_items_lalr(state,G)
            if any(map(lambda item:item.head == E and item.left == [T] and len(item.right) == 0,kernels)):
                target = state
                break
        
        assert target is not None
        kernels = ParserBuilder.get_kernel_items_lalr(target,G)
        for item in kernels:
            if item.head == E and item.left == [T]:
                assert item.lookaheads == { plus, G.end_symbol }
            elif item.head == T and item.left == [T]:
                assert mul in item.lookaheads
        
    def test_build_propagation_edges_1(self):
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),comodin_reductor
        G[E] += (T,),comodin_reductor

        G[T] += (id_,),comodin_reductor

        edges,lr0_states = ParserBuilder.build_lookaheads_propagation_edges(G)

        for state in edges:
            for (item,sym),(next_state_full,dest_item) in edges[state].items():
                expected = LR0Item(item.head,item.left + [sym],item.right[1:])
                assert dest_item.head == expected.head
                assert dest_item.left == expected.left
                assert dest_item.right == expected.right
                assert expected in ParserBuilder.get_kernel_items_lr0(next_state_full,G)
    
    def test_build_propagation_edges_2(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        edges,_ = ParserBuilder.build_lookaheads_propagation_edges(G)
        assert len(edges) == 1
    
    def test_goto_action_tables_1(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(S,L,R,mul,id_,eq,end_symbol) = classic_lalr_1_grammar

        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)
        states = ParserBuilder.get_canonical_lalr_states(G)

        accept_state = None
        for state in states:
            if any(
                map(
                    lambda item:item.head not in G.non_terminals and len(item.right) == 0 and item.left == [G.start_symbol],
                    state.items
                )
            ):
                accept_state = state
                break
        
        assert (accept_state,G.end_symbol) in action
        assert action[(accept_state,G.end_symbol)][0] == BottomUpParserAction.ACCEPT # type: ignore

        for state in states:
            if any(
                map(
                    lambda item: item.head==S and item.left == [R] and len(item.right) == 0,
                    state.items
                )
            ):
                assert action[(state,G.end_symbol)][0] == BottomUpParserAction.REDUCE
                assert action[((state,G.end_symbol))][1] == Production(S,[R])
            
            elif len(state.items) == 2:
                if any(
                    map(
                        lambda item: item.head == R and item.left == [L] and len(item.right) == 0,
                        state.items
                    )
                ):
                    assert action[(state,eq)][0] == BottomUpParserAction.SHIFT
                    assert action[(state,G.end_symbol)][0] == BottomUpParserAction.REDUCE
                    assert action[(state,G.end_symbol)][1] == Production(R,[L])
            
            elif len(state.items) == 1:
                item = next(iter(state.items))
                if item.head == R and item.left == [L] and len(item.right) == 0:
                    for sym in {G.end_symbol,eq}:
                        assert action[(state,sym)][0] == BottomUpParserAction.REDUCE
                        assert action[(state,sym)][1] == Production(R,[L])
    
    def test_goto_action_tables_2(self):
        E = Symbol('E')
        plus = Symbol('+',True)
        id_ = Symbol('id',True)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,E),comodin_reductor
        G[E] += (id_,),comodin_reductor

        with pytest.raises(LALRShiftReduceConflictException):
            _,_ = ParserBuilder.get_goto_action_tables_lalr(G)
    
    def test_goto_action_tables_3(self,conflict_reduce_reduce_lalr_1_grammar_1:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,_ = conflict_reduce_reduce_lalr_1_grammar_1

        with pytest.raises(LALRReduceReduceConflictException):
            _,_ = ParserBuilder.get_goto_action_tables_lalr(G)
    
    def test_cache_closure_lr0(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        item = LR0Item(S,[],[a])

        cl1 = ParserBuilder.closure_lr0({item},G)
        cl2 = ParserBuilder.closure_lr0({item},G)

        assert cl1 is cl2
    
    def test_cache_closure_lalr(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        item = LALRItem(S,[],[a],{G.end_symbol})

        cl1 = ParserBuilder.closure_lalr({item},G)
        cl2 = ParserBuilder.closure_lalr({item},G)

        assert cl1 is cl2
    
    def test_clear_cache_closure_1(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        item = LR0Item(S,[],[a])

        cl1 = ParserBuilder.closure_lr0({item},G)
        ParserBuilder.clear_cache()
        cl2 = ParserBuilder.closure_lr0({item},G)
        assert cl1 is not cl2
    
    def test_clear_cache_closure_2(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        item = LALRItem(S,[],[a],{G.end_symbol})

        cl1 = ParserBuilder.closure_lalr({item},G)
        ParserBuilder.clear_cache()
        cl2 = ParserBuilder.closure_lalr({item},G)

        assert cl1 is not cl2
    
    def test_cache_different_grammars_lr0(self):
        S = Symbol('S')
        a = Symbol('a',True)
        b = Symbol('b',True)

        G1 = AttributedGrammar(S,'$')
        G2 = AttributedGrammar(S,'$')

        G1[S] += (a,),comodin_reductor

        G2[S] += (b,),comodin_reductor

        item1 = LR0Item(S,[],[a])
        item2 = LR0Item(S,[],[b])
        cl1 = ParserBuilder.closure_lr0({item1},G1)
        cl2 = ParserBuilder.closure_lr0({item1},G2)
        assert cl1 is not cl2
        cl1 = ParserBuilder.closure_lr0({item2},G1)
        cl2 = ParserBuilder.closure_lr0({item2},G2)
        assert cl1 is not cl2
    
    def test_cyclic_grammar(self):
        A = Symbol('A')
        B = Symbol('B')

        G = AttributedGrammar(A,'$')

        G[A] += (B,),comodin_reductor
        G[B] += (A,),comodin_reductor

        states = ParserBuilder.get_canonical_lr0_states(G)
        assert len(states) > 0
        states = ParserBuilder.get_canonical_lalr_states(G)
        assert len(states) > 0
    
    def test_duplicated_productions(self):
        S = Symbol('S')
        a = Symbol('a',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor
        G[S] += (a,),comodin_reductor

        states = ParserBuilder.get_canonical_lr0_states(G)
        assert len(states) == 3
        states = ParserBuilder.get_canonical_lalr_states(G)
        assert len(states) == 3
    
    def test_unused_terminals(self):
        S = Symbol('S')
        a = Symbol('a',True)
        b = Symbol('b',True)

        G = AttributedGrammar(S,'$')

        G[S] += (a,),comodin_reductor

        states = ParserBuilder.get_canonical_lr0_states(G)

        for state in states:
            for item in state.items:
                assert b not in item.right

        states = ParserBuilder.get_canonical_lalr_states(G)

        for state in states:
            for item in state.items:
                assert b not in item.right

    def test_performance_lr0_1(self):
        S = Symbol('S')
        G = AttributedGrammar(S,'$')

        symbols = [Symbol(f'N{i}') for i in range(50)]
        id_ = Symbol('id',True)
        G[S] += (symbols[0],),comodin_reductor

        for i in range(49):
            G[symbols[i]] += (symbols[i + 1],),comodin_reductor
            G[symbols[i]] += (id_,),comodin_reductor

        G[symbols[49]] += (id_,),comodin_reductor

        start_time = time.time()
        states = ParserBuilder.get_canonical_lr0_states(G)
        elapsed = time.time() - start_time
        assert len(states) > 0
        assert elapsed < 2.0

    def test_performance_lalr_1(self):
        S = Symbol('S')
        G = AttributedGrammar(S,'$')

        symbols = [Symbol(f'N{i}') for i in range(50)]
        id_ = Symbol('id',True)
        G[S] += (symbols[0],),comodin_reductor

        for i in range(49):
            G[symbols[i]] += (symbols[i + 1],),comodin_reductor
            G[symbols[i]] += (id_,),comodin_reductor

        G[symbols[49]] += (id_,),comodin_reductor

        start_time = time.time()
        states = ParserBuilder.get_canonical_lalr_states(G)
        elapsed = time.time() - start_time
        assert len(states) > 0
        assert elapsed < 2.0
    
    def test_performance_lalr_2(self):
        S = Symbol('S')
        G = AttributedGrammar(S,'$')

        symbols = [Symbol(f'N{i}') for i in range(50)]
        id_ = Symbol('id',True)
        G[S] += (symbols[0],),comodin_reductor

        for i in range(49):
            G[symbols[i]] += (symbols[i + 1],),comodin_reductor

        G[symbols[49]] += (id_,),comodin_reductor

        start_time = time.time()
        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)
        elapsed = time.time() - start_time
        assert len(goto) > 0
        assert len(action) > 0
        assert elapsed < 2.0
    
    def test_goto_action_tables_correctness_1(self,arithmetic_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,end_symbol) = arithmetic_grammar

        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)

        # id
        tokens = [id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id + id
        tokens = [id_,plus,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id - id
        tokens = [id_,minus,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id % id
        tokens = [id_,mod,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id * id
        tokens = [id_,mul,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id / id
        tokens = [id_,div,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # id ** id
        tokens = [id_,exp,id_,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
        # ( id )
        tokens = [lp,id_,rp,end_symbol]
        assert self.simulate_parsing(tokens,goto,action)
    
    def test_goto_action_tables_correctness_2(self,arithmetic_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,(E,T,F,P,plus,minus,mul,div,exp,mod,lp,rp,id_,end_symbol) = arithmetic_grammar

        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)
        for _ in range(100):
            tokens = self.generate_valid_tokens_string(G) + [end_symbol]
            assert self.simulate_parsing(tokens,goto,action)
            index = randint(0,len(tokens) - 1)
            tokens.insert(index,tokens[index])
            assert not self.simulate_parsing(tokens,goto,action)
    
    def test_goto_action_tables_correctness_3(self,classic_lalr_1_grammar:Tuple[AttributedGrammar,Tuple[Symbol,...]]):
        G,_ = classic_lalr_1_grammar

        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)
        for _ in range(100):
            tokens = self.generate_valid_tokens_string(G) + [G.end_symbol]
            assert self.simulate_parsing(tokens,goto,action)
            index = randint(0,len(tokens) - 1)
            tokens.insert(index,tokens[index])
            assert not self.simulate_parsing(tokens,goto,action)