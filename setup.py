from setuptools import setup, find_packages
from Cython.Build import cythonize
from setuptools.extension import Extension

###################################################################################
#                                  COMON 
###################################################################################
common_extensions = Extension(
    name="pylgen.common.table",
    sources=[
        "pylgen/common/table.pyx",
    ]
)

common_types_extensions = Extension(
    name='pylgen.common.types',
    sources=[
        'pylgen/common/types.pyx'
    ]
)
###################################################################################
#                                  AUTOMATON
###################################################################################
automaton_extensions = Extension(
    name="pylgen.automaton.automaton",
    sources=[
        "pylgen/automaton/automaton.pyx"
    ]
)
###################################################################################
#                                  GRAMMAR
###################################################################################
grammar_extension = Extension(
    name='pylgen.grammar.grammar',
    sources=[
        'pylgen/grammar/grammar.pyx'
    ]
)
###################################################################################
#                                  REGEX
###################################################################################
regex_extensions = Extension(
    name='pylgen.regex.engine',
    sources=[
        'pylgen/regex/engine.pyx'
    ]
)
regex_parser_extensions = Extension(
    name='pylgen.regex.regex_parser',
    sources=[
        'pylgen/regex/regex_parser.pyx'
    ]
)
###################################################################################
#                                  PARSER
###################################################################################
parser_lr0_extensions = Extension(
    name='pylgen.parser.lr0_parser',
    sources=[
        'pylgen/parser/lr0_parser.pyx'
    ]
)
parser_lalr_extensions = Extension(
    name='pylgen.parser.lalr_parser',
    sources=[
        'pylgen/parser/lalr_parser.pyx'
    ]
)

parser_builder_extensions = Extension(
    name='pylgen.parser.parser_builder',
    sources=[
        'pylgen/parser/parser_builder.pyx'
    ]
)

parser_extensions = Extension(
    name='pylgen.parser.parser',
    sources=[
        'pylgen/parser/parser.pyx'
    ]
)
###################################################################################
#                                  LEXER
###################################################################################
base_lexer_extensions = Extension(
    name='pylgen.lexer.base_lexer',
    sources=[
        'pylgen/lexer/base_lexer.pyx'
    ]
)

lexer_extensions = Extension(
    name='pylgen.lexer.lexer',
    sources=[
        'pylgen/lexer/lexer.pyx'
    ]
)
###################################################################################

#                                  ANALYSIS
###################################################################################
error_extensions = Extension(
    name='pylgen.analysis.error',
    sources=[
        'pylgen/analysis/error.pyx'
    ]
)

lexical_rule_extension = Extension(
    name='pylgen.analysis.lexical',
    sources=[
        'pylgen/analysis/lexical.pyx',
    ]
)

visitor_extension = Extension(
    name='pylgen.analysis.visitor',
    sources=['pylgen/analysis/visitor.pyx']
)

context_extension = Extension(
    name='pylgen.analysis.context',
    sources=['pylgen/analysis/context.pyx']
)

setup(
    packages=[
        'pylgen',
        'pylgen.analysis',
        'pylgen.automaton',
        'pylgen.common',
        'pylgen.grammar',
        'pylgen.lexer',
        'pylgen.parser',
        'pylgen.regex',
        'pylgen.visual'
    ],
    ext_modules=cythonize([
        common_extensions,
        common_types_extensions,
        automaton_extensions,
        grammar_extension,
        regex_extensions,
        regex_parser_extensions,
        parser_lr0_extensions,
        parser_lalr_extensions,
        parser_builder_extensions,
        parser_extensions,
        base_lexer_extensions,
        lexer_extensions,
        error_extensions,
        lexical_rule_extension,
        visitor_extension,
        context_extension
    ])
)