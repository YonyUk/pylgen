from Cython.Build import cythonize
from setuptools import Extension,setup

###################################################################################
#                                  COMON 
###################################################################################
common_extensions = Extension(
    name="common.table",
    sources=[
        "common/table.pyx"
    ]
)

common_types_extensions = Extension(
    name='common.types',
    sources=[
        'common/types.pyx'
    ]
)
###################################################################################
#                                  AUTOMATON
###################################################################################
automaton_extensions = Extension(
    name="automaton.automaton",
    sources=[
        "automaton/automaton.pyx"
    ]
)
###################################################################################
#                                  GRAMMAR
###################################################################################
grammar_extension = Extension(
    name='grammar.grammar',
    sources=['grammar/grammar.pyx']
)
###################################################################################
#                                  REGEX
###################################################################################
regex_extensions = Extension(
    name='regex.engine',
    sources=[
        'regex/engine.pyx'
    ]
)
regex_parser_extensions = Extension(
    name='regex.regex_parser',
    sources=[
        'regex/regex_parser.pyx'
    ]
)
###################################################################################
#                                  PARSER
###################################################################################
parser_lr0_extensions = Extension(
    name='parser.lr0_parser',
    sources=[
        'parser/lr0_parser.pyx'
    ]
)
parser_lalr_extensions = Extension(
    name='parser.lalr_parser',
    sources=[
        'parser/lalr_parser.pyx'
    ]
)

parser_builder_extensions = Extension(
    name='parser.parser_builder',
    sources=[
        'parser/parser_builder.pyx'
    ]
)

parser_extensions = Extension(
    name='parser.parser',
    sources=[
        'parser/parser.pyx'
    ]
)
###################################################################################
#                                  LEXER
###################################################################################
lexer_extensions = Extension(
    name='lexer.lexer',
    sources=[
        'lexer/lexer.pyx'
    ]
)

setup(
    ext_modules=cythonize(common_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(common_types_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(automaton_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(grammar_extension),
    language_level=3
)

setup(
    ext_modules=cythonize(regex_extensions),
    language_level=3
)
setup(
    ext_modules=cythonize(regex_parser_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(parser_lr0_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(parser_lalr_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(parser_builder_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(parser_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(lexer_extensions),
    language_level=3
)