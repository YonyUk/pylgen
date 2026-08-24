from pylgen.visual.table import build_action_goto_slr_tables,build_action_goto_lalr_tables,build_action_goto_lr1_tables
from pylgen.common.types import Symbol
from pylgen.grammar import Grammar

import pytest

class TestVisualLrInspection:

    @pytest.fixture
    def classic_lalr_grammar(self) -> Grammar:
        S = Symbol('S')
        L = Symbol('L')
        R = Symbol('R')

        mul = Symbol('*',True)
        id_ = Symbol('id',True)
        eq = Symbol('=',True)

        G = Grammar(S,'$')

        G[S] += L,eq,R
        G[S] += R,

        G[L] += mul,R
        G[L] += id_,

        G[R] += L,

        return G

    @pytest.fixture
    def classic_lalr_grammar_with_reduce_reduce_conflict(self) -> Grammar:
        S = Symbol('S')
        L = Symbol('L')
        R = Symbol('R')

        mul = Symbol('*',True)
        id_ = Symbol('id',True)
        eq = Symbol('=',True)

        G = Grammar(S,'$')

        G[S] += L,eq,R
        G[S] += R,

        G[L] += mul,R
        G[L] += id_,

        G[R] += L,
        G[R] += id_,

        return G

    @pytest.fixture
    def classic_arithmetic_grammar(self) -> Grammar:
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        n = Symbol('n',True)

        G = Grammar(E,'$')

        G[E] += E,plus,T
        G[E] += T,

        G[T] += n,

        return G

    @pytest.fixture
    def classic_arithmetic_grammar_with_reduce_reduce_conflict(self) -> Grammar:
        E = Symbol('E')
        T = Symbol('T')

        plus = Symbol('+',True)
        n = Symbol('n',True)

        G = Grammar(E,'$')

        G[E] += E,plus,T
        G[E] += T,
        G[E] += n,

        G[T] += n,

        return G

    @pytest.fixture
    def lr1_grammar(self) -> Grammar:
        S = Symbol('S')
        A = Symbol('A')
        B = Symbol('B')

        a = Symbol('a',True)
        b = Symbol('b',True)
        c = Symbol('c',True)
        d = Symbol('d',True)
        e = Symbol('e',True)

        G = Grammar(S,'$')

        G[S] += a,A,d
        G[S] += b,B,d
        G[S] += a,B,e
        G[S] += b,A,e

        G[A] += c,
        G[B] += c,

        return G

    def test_lalr_tables_1(self,classic_lalr_grammar:Grammar):

        action,_ = build_action_goto_lalr_tables(classic_lalr_grammar)

        for (_,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                assert len(actions) == 1

    def test_slr_tables_1(self,classic_arithmetic_grammar:Grammar):

        action,_ = build_action_goto_slr_tables(classic_arithmetic_grammar)

        for (_,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                assert len(actions) == 1

    def test_lr1_tables_1(self,classic_arithmetic_grammar:Grammar):

        action,_ = build_action_goto_lr1_tables(classic_arithmetic_grammar)

        for (_,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                assert len(actions) == 1

    def test_lalr_tables_2(self,classic_lalr_grammar_with_reduce_reduce_conflict:Grammar):
        action,_ = build_action_goto_lalr_tables(classic_lalr_grammar_with_reduce_reduce_conflict)

        for (state,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                if state.index == 3 and (symbol.symbol == '=' or symbol.symbol == '$'):
                    assert len(actions) == 2
                    assert actions[0][0] == actions[1][0]
                else:
                    assert len(actions) == 1

    def test_lr1_tables_2(self,lr1_grammar:Grammar):

        action,_ = build_action_goto_lr1_tables(lr1_grammar)

        for (_,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                assert len(actions) == 1

    def test_slr_tables_2(self,classic_lalr_grammar:Grammar):

        action,_ = build_action_goto_slr_tables(classic_lalr_grammar)

        for (state,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                if state.index == 5 and symbol.symbol == '=':
                    assert len(actions) == 2
                    assert actions[0][0] != actions[1][0]
                else:
                    assert len(actions) == 1

    def test_lr1_tables_3(self,classic_lalr_grammar:Grammar):
    
        action,_ = build_action_goto_lr1_tables(classic_lalr_grammar)

        for (_,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                assert len(actions) == 1

    def test_lalr_tables_3(self):
        E = Symbol('E')
        n = Symbol('n',True)
        plus = Symbol('+',True)

        G = Grammar(E,'$')

        G[E] += E,plus,E
        G[E] += n,

        action,_ = build_action_goto_lalr_tables(G)

        for (state,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                if state.index == 4 and symbol.symbol == '+':
                    assert len(actions) == 2
                    assert actions[0][0] != actions[1][0]
                else:
                    assert len(actions) == 1

    def test_slr_tables_3(self,classic_arithmetic_grammar_with_reduce_reduce_conflict:Grammar):

        action,_ = build_action_goto_slr_tables(classic_arithmetic_grammar_with_reduce_reduce_conflict)

        for (state,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                if state.index == 2 and (symbol.symbol == '+' or symbol.symbol == '$'):
                    assert len(actions) == 2
                    assert actions[0][0] == actions[1][0]
                else:
                    assert len(actions) == 1

    def test_lr1_tables_4(self):
        E = Symbol('E')
        n = Symbol('n',True)
        plus = Symbol('+',True)

        G = Grammar(E,'$')

        G[E] += E,plus,E
        G[E] += n,

        action,_ = build_action_goto_lr1_tables(G)

        for (state,symbol),actions in action.items():
            if not symbol.is_terminal:
                continue
            if actions:
                if state.index == 4 and symbol.symbol == '+':
                    assert len(actions) == 2
                    assert actions[0][0] != actions[1][0]
                else:
                    assert len(actions) == 1