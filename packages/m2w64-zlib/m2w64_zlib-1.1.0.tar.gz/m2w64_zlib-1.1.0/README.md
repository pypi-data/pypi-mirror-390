# Zlib Compressor

A Python package for compression and decompression using zlib.dll via ctypes.

## ⚠️ Important Notice

**This package uses external zlib.dll dependency** - please read this section carefully.

This package provides Python bindings for zlib compression library using ctypes. It requires `zlib.dll` which is **not included** in the package. You need to provide zlib.dll separately.

### About zlib.dll

zlib.dll is the dynamic link library version of the popular zlib compression library. This package uses ctypes to interact directly with the zlib.dll file.

### How to Get zlib.dll

You can obtain zlib.dll from several sources:

1. **Official zlib website**: http://www.zlib.net/
2. **GitHub repositories** with pre-built Windows binaries
3. **Package managers** like vcpkg or MSYS2

### Example download from GitHub (unofficial source):

```bash
# Example using curl to download from a GitHub repository
curl -L -o zlib.dll https://github.com/msg3176357131/zlib/raw/main/zlib.dll