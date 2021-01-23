from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("cython_utils.pyx", language_level=3)
)

# use this line to compile :
# python setupCythonUtils.py build_ext --inplace