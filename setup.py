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
base_lexer_extensions = Extension(
    name='lexer.base_lexer',
    sources=[
        'lexer/base_lexer.pyx'
    ]
)

lexer_extensions = Extension(
    name='lexer.lexer',
    sources=[
        'lexer/lexer.pyx'
    ]
)
###################################################################################
#                                  ANALISIS
###################################################################################
error_extensions = Extension(
    name='analisis.error',
    sources=[
        'analisis/error.pyx'
    ]
)

lexical_rule_extension = Extension(
    name='analisis.lexical',
    sources=[
        'analisis/lexical.pyx'
    ]
)

visitor_extension = Extension(
    name='analisis.visitor',
    sources=['analisis/visitor.pyx']
)

context_extension = Extension(
    name='analisis.context',
    sources=['analisis/context.pyx']
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
    ext_modules=cythonize(base_lexer_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(lexer_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(error_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(lexical_rule_extension),
    language_level=3
)

setup(
    ext_modules=cythonize(visitor_extension),
    language_level=3
)

setup(
    ext_modules=cythonize(context_extension),
    language_level=3
)