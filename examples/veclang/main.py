import os
from sys import argv

from veclang.lexer import build_lexer
from veclang.tokens_enum import TokenTypeEnum
from veclang.parser import build_parser
from veclang.visitors import build_walkers,get_ast_value

lexer = build_lexer()
VecLangParser = build_parser()
context,error_collector,functions_collector,evaluator = build_walkers()

if len(argv) < 2:
    raise ValueError('not input provided')

file = argv[1]

if not (os.path.exists(file) or os.path.isfile(file)):
    raise ValueError('Invalid argument')


lexer.set_eof_token('\x00',TokenTypeEnum.EOF)
lexer.initialize()

with open(file,'r') as f:
    text = f.read()
    lexer.load_text(text)
    ast = VecLangParser.parse(lexer.tokens)
    errors = []
    errors += list(lexer.errors)
    errors += VecLangParser.errors

    if not errors:
        functions_collector.walk(ast)

    if not errors:
        error_collector.walk(ast)

    errors += context.errors

    if not errors:
        evaluator.walk(ast)
        errors += context.errors

    if not errors:
        result = get_ast_value(ast,context)
        if result is not None:
            print(result)

    if errors:
        for error in errors:
            print(error)