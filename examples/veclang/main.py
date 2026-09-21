import os
from sys import argv

from veclang.lexer import build_lexer
from veclang.parser import build_parser
from veclang.visitors import build_walkers,get_ast_value

from datetime import datetime

def get_fragment(text:str,start:tuple[int,int],end:tuple[int,int]) -> str:

    result = ''
    reading = False
    lines = text.splitlines()
    for index,line in enumerate(lines):
        if index == start[0] - 1:
            if start[0] == end[0]:
                return line[start[1] - 1:end[1] - 1]
            result += line[start[1] - 1:]
            reading = True
        elif reading:
            result += line
        elif index == end[0] - 1:
            result += line[:end[1] - 1]
            return result

    return ''

t = datetime.now()
lexer = build_lexer()
print('lexer builded in',datetime.now() - t)
t = datetime.now()
lexer.initialize()
print('lexer initialized in',datetime.now() - t)
t = datetime.now()
VecLangParser = build_parser()
print('parser builded in',datetime.now() - t)
context,error_collector,functions_collector,evaluator = build_walkers()

if len(argv) < 2:
    raise ValueError('not input provided')

file = argv[1]

if not (os.path.exists(file) or os.path.isfile(file)):
    raise ValueError('Invalid argument')

help_flag = False
if len(argv) >= 3 and argv[2] == '--help':
    from pylgen.visual import set_cache_file,draw_ast
    help_flag = True
    set_cache_file('cache')

with open(file,'r') as f:
    text = f.read()
    lexer.load_text(text)
    t = datetime.now()
    ast = VecLangParser.parse(lexer.tokens)
    print('source parsed in',datetime.now() - t)
    errors = []
    errors += list(lexer.errors)
    errors += VecLangParser.errors

    if not errors:
        if help_flag:
            draw_ast(ast,show=True,cache=True,select_menu=True) # type: ignore
        t = datetime.now()
        functions_collector.walk(ast)
        print('functions collected in',datetime.now() - t)

    if not errors:
        t = datetime.now()
        error_collector.walk(ast)
        print('errors collected in',datetime.now() - t)

    errors += context.errors

    if not errors:
        t = datetime.now()
        evaluator.walk(ast)
        print('code evaluated in',datetime.now() - t)
        errors += context.errors

    if not errors:
        result = get_ast_value(ast,context)
        if result is not None:
            print(result)

    if errors:
        for error in errors:
            print(error)
            print('\tloc:',get_fragment(text,error.start_position,error.end_position))

