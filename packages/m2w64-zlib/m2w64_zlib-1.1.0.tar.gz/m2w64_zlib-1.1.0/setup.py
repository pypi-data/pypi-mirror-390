from setuptools import setup, find_packages
import os
from m2w64zlib._get_zlib_dll import _get_from_github

_get_from_github()

setup(
    name="m2w64-zlib",
    version="1.1.0",
    author="Julia Venson",
    author_email="jv1995vensonsl@proton.com",
    description="A Python package for compression and decompression using zlib.dll",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="compression, decompression, zlib, dll, data-compression",
)