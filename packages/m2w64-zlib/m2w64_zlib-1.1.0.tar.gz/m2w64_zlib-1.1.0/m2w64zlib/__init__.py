"""
Zlib Compressor - A Python package for compression and decompression using zlib.dll
"""

from .compressor import ZlibCompressor
from .tests import _test_compression

__version__ = "1.1.0"
__author__ = "Julia Venson"
__email__ = "jv1995vensonsl@proton.com"

__all__ = ["ZlibCompressor", "_test_compression"]