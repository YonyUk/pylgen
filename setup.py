from Cython.Build import cythonize
from setuptools import Extension,setup

common_extensions = Extension(
    name="common.table",
    sources=[
        "common/table.pyx"
    ]
)

automaton_extensions = Extension(
    name="automaton.automaton",
    sources=[
        "automaton/automaton.pyx"
    ]
)

setup(
    ext_modules=cythonize(common_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(automaton_extensions),
    language_level=3
)