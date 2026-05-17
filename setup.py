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

setup(
    ext_modules=cythonize(common_extensions),
    language_level=3
)

setup(
    ext_modules=cythonize(common_types_extensions),
    language_level=3
)