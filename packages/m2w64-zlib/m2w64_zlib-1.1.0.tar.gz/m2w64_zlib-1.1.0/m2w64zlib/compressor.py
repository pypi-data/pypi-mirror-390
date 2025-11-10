import ctypes
import os
import platform


class ZlibCompressor:
    """Class for data compression and decompression using zlib.dll"""

    def __init__(self, dll_path=None):
        """
        Initialize the compressor

        Args:
            dll_path (str): Path to zlib.dll
        """
        if dll_path is None:
            dll_path = r"C:\tmp\zlib.dll"

        self.dll_path = os.path.abspath(dll_path)
        self._load_dll()
        self._setup_functions()

    def _load_dll(self):
        """Load zlib.dll"""
        try:
            self.zlib = ctypes.CDLL(self.dll_path)
            print("zlib.dll loaded successfully!")
        except Exception as e:
            raise Exception(f"Error loading zlib.dll: {e}")

    def _setup_functions(self):
        """Configure DLL functions"""
        # compress2
        self.zlib.compress2.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),  # dest
            ctypes.POINTER(ctypes.c_ulong),  # destLen
            ctypes.POINTER(ctypes.c_ubyte),  # source
            ctypes.c_ulong,  # sourceLen
            ctypes.c_int  # level
        ]
        self.zlib.compress2.restype = ctypes.c_int

        # uncompress
        self.zlib.uncompress.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),  # dest
            ctypes.POINTER(ctypes.c_ulong),  # destLen
            ctypes.POINTER(ctypes.c_ubyte),  # source
            ctypes.c_ulong  # sourceLen
        ]
        self.zlib.uncompress.restype = ctypes.c_int

    def compress(self, data, compression_level=6):
        """
        Compress data

        Args:
            data: Data to compress (str or bytes)
            compression_level (int): Compression level (0-9)

        Returns:
            bytes: Compressed data
        """
        # Convert data to bytes
        if isinstance(data, str):
            data = data.encode('utf-8')

        data_bytes = bytes(data)
        src_len = len(data_bytes)

        # Calculate maximum compressed data size
        dest_len = ctypes.c_ulong(src_len + (src_len // 100) + 12)
        dest_buf = (ctypes.c_ubyte * dest_len.value)()

        # Create pointers
        src_buf = (ctypes.c_ubyte * src_len).from_buffer_copy(data_bytes)

        # Compress data
        result = self.zlib.compress2(
            dest_buf,
            ctypes.byref(dest_len),
            src_buf,
            src_len,
            compression_level
        )

        if result == 0:  # Z_OK
            compressed_data = bytes(dest_buf[:dest_len.value])
            return compressed_data
        else:
            raise Exception(f"Compression error: {result}")

    def decompress(self, compressed_data, original_size=None):
        """
        Decompress data

        Args:
            compressed_data (bytes): Compressed data
            original_size (int): Estimated original data size

        Returns:
            bytes: Decompressed data
        """
        comp_len = len(compressed_data)

        # If original size not specified, assume 10 times larger
        if original_size is None:
            original_size = comp_len * 10

        dest_len = ctypes.c_ulong(original_size)
        dest_buf = (ctypes.c_ubyte * dest_len.value)()

        # Create pointer to compressed data
        comp_buf = (ctypes.c_ubyte * comp_len).from_buffer_copy(compressed_data)

        # Decompress
        result = self.zlib.uncompress(
            dest_buf,
            ctypes.byref(dest_len),
            comp_buf,
            comp_len
        )

        if result == 0:  # Z_OK
            decompressed_data = bytes(dest_buf[:dest_len.value])
            return decompressed_data
        else:
            # Try with larger size
            if result == -5:  # Z_BUF_ERROR
                return self.decompress(compressed_data, original_size * 2)
            raise Exception(f"Decompression error: {result}")

    def compress_file(self, input_file, output_file, compression_level=6):
        """
        Compress a file

        Args:
            input_file (str): Path to input file
            output_file (str): Path for output compressed file
            compression_level (int): Compression level
        """
        try:
            if not platform.system().lower() == 'windows':
                print("This package requires Windows OS. Current system:", platform.system())
                return False

            if not os.path.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")

            with open(input_file, 'rb') as f:
                original_data = f.read()

            compressed_data = self.compress(original_data, compression_level)

            with open(output_file, 'wb') as f:
                f.write(compressed_data)

            original_size = len(original_data)
            compressed_size = len(compressed_data)
            ratio = (1 - compressed_size / original_size) * 100

            print(f"File compressed: {input_file} → {output_file}")
            print(f"Compression: {original_size} → {compressed_size} bytes ({ratio:.1f}%)")
        except Exception as e:
            print(e)

    def decompress_file(self, input_file, output_file):
        """
        Decompress a file

        Args:
            input_file (str): Path to compressed file
            output_file (str): Path for decompressed file
        """
        try:
            if not platform.system().lower() == 'windows':
                print("This package requires Windows OS. Current system:", platform.system())
                return False

            if not os.path.exists(input_file):
                raise FileNotFoundError(f"File not found: {input_file}")

            with open(input_file, 'rb') as f:
                compressed_data = f.read()

            decompressed_data = self.decompress(compressed_data)

            with open(output_file, 'wb') as f:
                f.write(decompressed_data)

            print(f"File decompressed: {input_file} → {output_file}")
            print(f"Size: {len(decompressed_data)} bytes")
        except Exception as e:
            print(e)