from setuptools import setup
from Cython.Build import cythonize


setup(name="CFilter",version="0.1",
    ext_modules = cythonize("CFilter.pyx", language_level=3)
)

# use this line to compile :
# python setupCFilter.py build_ext --inplace