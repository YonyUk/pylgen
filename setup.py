from setuptools import setup, find_packages
from Cython.Build import cythonize
from setuptools.extension import Extension

requirements = [
    "asttokens==3.0.1",
    "build==1.5.0",
    "colorama==0.4.6",
    "contourpy==1.3.3",
    "cycler==0.12.1",
    "Cython==3.2.4",
    "decorator==5.2.1",
    "executing==2.2.1",
    "fonttools==4.62.1",
    "iniconfig==2.3.0",
    "ipython==9.13.0",
    "ipython_pygments_lexers==1.1.1",
    "jedi==0.20.0",
    "Jinja2==3.1.6",
    "jsonpickle==4.1.1",
    "kiwisolver==1.5.0",
    "MarkupSafe==3.0.3",
    "matplotlib==3.10.9",
    "matplotlib-inline==0.2.2",
    "narwhals==2.21.2",
    "networkx==3.6.1",
    "numpy==2.4.4",
    "packaging==26.2",
    "parso==0.8.7",
    "pillow==12.2.0",
    "pluggy==1.6.0",
    "prompt_toolkit==3.0.52",
    "psutil==7.2.2",
    "pure_eval==0.2.3",
    "Pygments==2.20.0",
    "pyparsing==3.3.2",
    "pyproject_hooks==1.2.0",
    "pytest==9.0.3",
    "python-dateutil==2.9.0.post0",
    "pyvis==0.3.2",
    "PyYAML==6.0.3",
    "setuptools==82.0.1",
    "six==1.17.0",
    "stack-data==0.6.3",
    "tornado==6.5.5",
    "traitlets==5.15.0",
    "wcwidth==0.7.0",
    "wheel==0.47.0",
    "xyzservices==2026.3.0"
]

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
#                                  ANALISIS
###################################################################################
error_extensions = Extension(
    name='pylgen.analisis.error',
    sources=[
        'pylgen/analisis/error.pyx'
    ]
)

lexical_rule_extension = Extension(
    name='pylgen.analisis.lexical',
    sources=[
        'pylgen/analisis/lexical.pyx',
    ]
)

visitor_extension = Extension(
    name='pylgen.analisis.visitor',
    sources=['pylgen/analisis/visitor.pyx']
)

context_extension = Extension(
    name='pylgen.analisis.context',
    sources=['pylgen/analisis/context.pyx']
)

setup(
    name='pylgen',
    version='0.3.3',
    description='test',
    author='YonyUk',
    packages=[
        'pylgen',
        'pylgen.analisis',
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
    ]),
    install_requires=requirements,
    python_requires=">=3.13.7"
)