from setuptools.extension import Extension
from setuptools import setup
from Cython.Build import cythonize

interpreter_extensions = Extension(
    name='veclang.parser',
    sources=[
        'veclang/parser.pyx'
    ]
)

asts_extensions = Extension(
    name='veclang.asts',
    sources=[
        'veclang/asts.pyx'
    ]
)

visitors_extensions = Extension(
    name='veclang.visitors',
    sources=[
        'veclang/visitors.pyx'
    ]
)

errors_extension = Extension(
    name='veclang.errors',
    sources=[
        'veclang/errors.pyx'
    ]
)

lexer_extensions = Extension(
    name='veclang.lexer',
    sources=[
        'veclang/lexer.pyx'
    ]
)

setup(
    ext_modules=cythonize([
        interpreter_extensions,
        asts_extensions,
        visitors_extensions,
        errors_extension,
        lexer_extensions
    ]),
    language_level=3
)