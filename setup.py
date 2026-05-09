from Cython.Build import cythonize
from setuptools import Extension,setup

common_extensions = Extension(
    name="common.table",
    sources=[
        "common/table.pyx"
    ]
)

setup(
    ext_modules=cythonize(common_extensions),
    language_level=3
)