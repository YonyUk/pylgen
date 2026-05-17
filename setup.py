from Cython.Build import cythonize
from setuptools import Extension,setup

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

automaton_extensions = Extension(
    name="automaton.automaton",
    sources=[
        "automaton/automaton.pyx"
    ]
)

attributed_grammar_extensions = Extension(
    name='grammar.attributed_grammar',
    sources=[
        'grammar/attributed_grammar.pyx'
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
    ext_modules=cythonize(attributed_grammar_extensions),
    language_level=3
)