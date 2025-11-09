from setuptools import setup, Extension
from Cython.Build import cythonize
import os

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="b64fx",
    version="1.0",
    description="Base16/32/64/85 and Ascii85 encoding/decoding (Cython compiled)",
    author="Anonymous",
    ext_modules=cythonize(
        Extension(
            "b64fx",
            [os.path.join(here, "b64fx.pyx")]
        ),
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': True,
            'cdivision': True
        }
    ),
    packages=[],
    zip_safe=False,
)