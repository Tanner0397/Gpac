"""
Tanner Wendland
CS5401

Used for building cython code
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'Gpac Tanner Wendland',
    ext_modules = cythonize(["src/cython/*.pyx"], build_dir="build", language='c++')
)
