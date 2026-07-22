from pylgen.parser.parser import ParsingException

from arithmetic_interpreter.grammar import parser
from arithmetic_interpreter.lexer import lexer
from arithmetic_interpreter.semantic import context,evaluator_ast_walker,error_collector_ast_walker

while True:
    context.clear_garbage()
    parser.reset()
    lexer.clear_errors()
    
    text = input('>>> ')
    if len(text) == 0:
        continue
    lexer.load_text(text)
    try:
        ast = parser.parse(lexer.tokens)
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
        if result is not None:
            print(result)