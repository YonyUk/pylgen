from argparse import ArgumentParser
from idented_dsl.lexer import lexer
from idented_dsl.grammar import parser
from idented_dsl.codegen import to_json

import os

arg_parser = ArgumentParser()
arg_parser.add_argument('-input','-i',help='file input',required=True)
arg_parser.add_argument('-draw','-d',help='draw the result ast',default=False,required=False,action='store_true')
arg_parser.add_argument('-cache','-c',help='especify the cache file an use it (ONLY VALID WITH -d flag)',required=False)
arg_parser.add_argument('-output','-o',help='output file',default='out.json',required=False)
args = arg_parser.parse_args()

file = args.input
draw_flag = args.draw
cache = args.cache
output_file = args.output

if not os.path.exists(file) or not os.path.isfile(file):
    raise ValueError()

with open(file,'r') as f:
    lexer.load_text(f.read())
    ast = parser.parse(lexer.tokens)
    errors = list(lexer.errors) + parser.errors
    if errors:
        for error in errors:
            print(error)
    elif draw_flag:
        if cache and (not os.path.exists(cache) or not os.path.isfile(cache)):
            raise ValueError()
        from pylgen.visual import draw_ast,set_cache_file

        if cache:
            set_cache_file(cache)
        draw_ast(ast,show=True,cache=True if cache else False)

    if not errors:
        json = to_json(ast)
        with open(output_file,'w') as f:
            f.write(json)