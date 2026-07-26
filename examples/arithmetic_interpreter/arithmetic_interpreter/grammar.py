from pylgen.parser.parser import BottomUpParser
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.grammar.grammar import AttributedGrammar
from .grammar_symbols import (
    END_SYMBOL,
    VAR,
    ArithmeticExpression,
    E,
    T,
    F,
    P,
    plus,
    minus,
    mul,
    div,
    exp,
    mod,
    lp,
    rp,
    number,
    variable,
    eq,
    exit,
    clear
)
from .reductors import (
    binary_reductor,
    single_reductor,
    parenthesis_reductor,
    variable_reductor,
    exit_reductor,
    clear_reductor
)

# Create the attributed grammar with the start symbol and end marker
G = AttributedGrammar(ArithmeticExpression, END_SYMBOL)

G[ArithmeticExpression] += (E,), single_reductor
G[ArithmeticExpression] += (VAR, eq, E), binary_reductor
G[ArithmeticExpression] += (exit, lp, rp), exit_reductor
G[ArithmeticExpression] += (clear, lp, rp), clear_reductor

G[E] += (E, plus, T), binary_reductor
G[E] += (E, minus, T), binary_reductor
G[E] += (T,), single_reductor

G[T] += (T, mul, F), binary_reductor
G[T] += (T, div, F), binary_reductor
G[T] += (T, mod, F), binary_reductor
G[T] += (F,), single_reductor

G[F] += (F, exp, P), binary_reductor
G[F] += (P,), single_reductor

G[P] += (lp, E, rp), parenthesis_reductor
G[P] += (number,), single_reductor
G[P] += (VAR,), single_reductor

G[VAR] += (variable,), variable_reductor

parser = ParserBuilder.build_parser_from_attributed(G, ParserType.LALR1)