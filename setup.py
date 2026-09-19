from setuptools import setup, find_packages
from Cython.Build import cythonize
from setuptools.extension import Extension

COMPILER_DIRECTIVES = {
    'binding': True,
    'boundscheck': True,
    'nonecheck': False,
    'initializedcheck': True,
    'freethreading_compatible': False,
    'subinterpreters_compatible': 'no',
    'embedsignature': False,
    'embedsignature.format': 'c',
    'auto_cpdef': False,
    'auto_pickle': None,
    'cdivision': False,
    'cdivision_warnings': False,
    'cpow': None,
    'c_api_binop_methods': False,
    'overflowcheck': False,
    'overflowcheck.fold': True,
    'always_allow_keywords': True,
    'allow_none_for_extension_args': True,
    'wraparound': True,
    'ccomplex': False,
    'callspec': '',
    'nogil': False,
    'gil': False,
    'with_gil': False,
    'profile': False,
    'linetrace': False,
    'emit_code_comments': True,
    'annotation_typing': True,
    'infer_types': None,
    'infer_types.verbose': False,
    'autotestdict': True,
    'autotestdict.cdef': False,
    'autotestdict.all': False,
    'language_level': None,
    'fast_getattr': False,
    'py2_import': False,
    'preliminary_late_includes_cy28': False,
    'iterable_coroutine': False,
    'c_string_type': 'bytes',
    'c_string_encoding': '',
    'type_version_tag': True,
    'unraisable_tracebacks': True,
    'old_style_globals': False,
    'np_pythran': False,
    'fast_gil': False,
    'cpp_locals': False,
    'legacy_implicit_noexcept': False,
    'c_compile_guard': '',
    'set_initial_path': None,
    'warn': None,
    'warn.undeclared': False,
    'warn.unreachable': True,
    'warn.maybe_uninitialized': False,
    'warn.unused': False,
    'warn.unused_arg': False,
    'warn.unused_result': False,
    'warn.multiple_declarators': True,
    'warn.deprecated.DEF': False,
    'warn.deprecated.IF': True,
    'show_performance_hints': True,
    'optimize.inline_defnode_calls': True,
    'optimize.unpack_method_calls': True,
    'optimize.unpack_method_calls_in_pyinit': False,
    'optimize.use_switch': True,
    'remove_unreachable': True,
    'control_flow.dot_output': '',
    'control_flow.dot_annotate_defs': False,
    'test_assert_path_exists': [],
    'test_fail_if_path_exists': [],
    'test_body_needs_exception_handling': None,
    'test_assert_c_code_has': [],
    'test_fail_if_c_code_has': [],
    'formal_grammar': False
}

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

parser_lr1_extensions = Extension(
    name='pylgen.parser.lr1_parser',
    sources=[
        'pylgen/parser/lr1_parser.pyx'
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
        parser_lr1_extensions,
        parser_lalr_extensions,
        parser_builder_extensions,
        parser_extensions,
        base_lexer_extensions,
        lexer_extensions,
        lexical_rule_extension,
        visitor_extension,
        context_extension
    ],
    compiler_directives=COMPILER_DIRECTIVES,
    force=True
    )
)