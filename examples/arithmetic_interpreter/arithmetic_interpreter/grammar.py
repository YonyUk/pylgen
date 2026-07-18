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

G3 = AttributedGrammar(ArithmeticExpression,END_SYMBOL)

G3[ArithmeticExpression] += (E,),single_reductor
G3[ArithmeticExpression] += (VAR,eq,E),binary_reductor
G3[ArithmeticExpression] += (exit,lp,rp),exit_reductor
G3[ArithmeticExpression] += (clear,lp,rp),clear_reductor

G3[E] += (E,plus,T),binary_reductor
G3[E] += (E,minus,T),binary_reductor
G3[E] += (T,),single_reductor


G3[T] += (T,mul,F),binary_reductor
G3[T] += (T,div,F),binary_reductor
G3[T] += (T,mod,F),binary_reductor
G3[T] += (F,),single_reductor

G3[F] += (F,exp,P),binary_reductor
G3[F] += (P,),single_reductor

G3[P] += (lp,E,rp),parenthesis_reductor
G3[P] += (number,),single_reductor
G3[P] += (VAR,),single_reductor

G3[VAR] += (variable,),variable_reductor

parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1) # type: ignore