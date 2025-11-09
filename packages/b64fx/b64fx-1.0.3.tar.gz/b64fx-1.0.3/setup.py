from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Компилируем b64fx.c (не .pyx) для PyPI
ext_modules = cythonize(
    Extension(
        "b64fx",
        sources=["b64fx.c"],  # используем уже сгенерированный .c
    ),
    compiler_directives={
        "language_level": "3",
        "boundscheck": False,
        "wraparound": True,
        "cdivision": True
    }
)

setup(
    name="b64fx",
    version="1.0.3",  # увеличиваем версию
    description="Base16/32/64/85 and Ascii85 encoding/decoding (Cython compiled)",
    author="Anonymous",
    ext_modules=ext_modules,
    zip_safe=False,
)