from typing import Iterable

from pylgen.common.types import Symbol,Token
from pylgen.common.enums import TokenType
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.parser.parser import BottomUpParser,ParsingException
from pylgen.lexer.lexer import Lexer
from pylgen.analisis.lexical import LexicRule
from pylgen.automaton.automaton import DFA
from pylgen.analisis.visitor import ASTWalker
from pylgen.visual import set_cache_file,draw_ast,draw_parse_tree_from_parser

from arithmetic_interpreter.context import ArithmeticExpressionContext
from arithmetic_interpreter.visitors import (
    ClearASTEvaluatorVisitor,
    PostOrderStrategy,
    ArithmeticExpressionASTChildrenSelector,
    DivASTSemanticErrorCollectorVisitor,
    ModASTSemanticErrorCollectorVisitor,
    VariableASTSemanticErrorCollectorVisitor,
    AssigmentASTSemanticErrorCollectorVisitor,
    PlusASTEvaluatorVisitor,
    MinusASTEvaluatorVisitor,
    MulASTEvaluatorVisitor,
    DivASTEvaluatorVisitor,
    ExpASTEvaluatorVisitor,
    ModASTEvaluatorVisitor,
    AtomicASTEvaluatorVisitor,
    AssigmentASTEvaluatorVisitor,
    ExitASTEvaluatorVisitor
)
from arithmetic_interpreter.asts import (
    AssigmentAST,
    ClearAST,
    PlusAST,
    MinusAST,
    MulAST,
    DivAST,
    ExpAST,
    ModAST,
    VarAST,
    ExitAST
)
from arithmetic_interpreter.grammar_symbols import END_SYMBOL,number,variable
from arithmetic_interpreter.grammar import G3

context = ArithmeticExpressionContext()
traversal_strategy = PostOrderStrategy()

traversal_strategy.set_default_selector(ArithmeticExpressionASTChildrenSelector())

error_collector_ast_walker = ASTWalker(context,traversal_strategy)

error_collector_ast_walker.add_visitor(DivAST,DivASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(ModAST,ModASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(VarAST,VariableASTSemanticErrorCollectorVisitor())
error_collector_ast_walker.add_visitor(AssigmentAST,AssigmentASTSemanticErrorCollectorVisitor())

evaluator_ast_walker = ASTWalker(context,traversal_strategy)

evaluator_ast_walker.add_visitor(PlusAST,PlusASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(MinusAST,MinusASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(MulAST,MulASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(DivAST,DivASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ExpAST,ExpASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ModAST,ModASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(Token,AtomicASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(AssigmentAST,AssigmentASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ExitAST,ExitASTEvaluatorVisitor())
evaluator_ast_walker.add_visitor(ClearAST,ClearASTEvaluatorVisitor())

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'
    OPERATOR = 'OPERATOR'
    VARIABLE = 'VARIABLE'
    KEYWORD = 'KEYWORD'

class NumberLexicRule(LexicRule):

    def __init__(self) -> None:
        super().__init__('number must be 0 or star with a non-zero digit')
    
    def _check(self, text: str):
        if '.' in text:
            return str(float(text)) == text
        return str(int(text)) == text

class VariableLexicRule(LexicRule):

    def __init__(self) -> None:
        super().__init__('variables names can\'t star with a number')
    
    def _check(self, text: str):
        return not text[0].isdigit()

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.KEYWORD:
        return Symbol(tx,True)
    return Symbol(tx,True)

def get_tokens(end_symbol:Symbol,tokens:Iterable[Token]):
    line = 0
    column = 0
    for token in tokens:
        line = token.line
        column = token.column
        yield token
    yield Token(end_symbol.symbol,TokenTypeEnum.SYMBOL,end_symbol,line,column + 1)

ignore_dfa = DFA('start','start',{' ','\n','\t'},True)
ignore_dfa += ignore_dfa.start_state,' ',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\n',ignore_dfa.start_state
ignore_dfa += ignore_dfa.start_state,'\t',ignore_dfa.start_state

lexer = Lexer(get_symbol_function,ignore_dfa)
lexer[0,TokenTypeEnum.NUMBER] = '\\d+|\\d+\\.\\d+'
lexer[1,TokenTypeEnum.SYMBOL] = '\\(|\\)'
lexer[2,TokenTypeEnum.OPERATOR] = '\\+|\\*\\*?|\\-|/|%|='
lexer[3,TokenTypeEnum.KEYWORD] = 'exit|clear'
lexer[4,TokenTypeEnum.VARIABLE] = '\\w+'

lexer.add_rule(TokenTypeEnum.NUMBER,NumberLexicRule())
lexer.add_rule(TokenTypeEnum.VARIABLE,VariableLexicRule())

parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1) # type: ignore

# set_cache_file('cache')
while True:
    context.clear_garbage()
    parser.reset()
    lexer.clear_errors()
    
    text = input('>>> ')
    if len(text) == 0:
        continue
    lexer.load_text(text)
    try:
        ast = parser.parse(get_tokens(Symbol(END_SYMBOL,True),lexer.tokens))
        error_collector_ast_walker.walk(ast)
        # draw_parse_tree_from_parser(parser,filename='parse_tree',show=True,cache=True)
        # draw_ast(ast,filename='ast',show=True,cache=True)
        if not context.errors:
            evaluator_ast_walker.walk(ast)
    except ParsingException:
        pass

    errors = list(lexer.errors) + parser.errors + context.errors
    if errors:
        for error in errors:
            print(error)
    else:
        result = context.get_ast_value(ast) # type: ignore
        if result:
            print(result)