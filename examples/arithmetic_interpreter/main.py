from pylgen.common.types import Symbol,Token
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.parser.parser import BottomUpParser,ParsingException
from pylgen.analysis.visitor import ASTWalker

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
from arithmetic_interpreter.lexer import lexer,get_tokens

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

parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G3,ParserType.LALR1) # type: ignore

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