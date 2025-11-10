import os

from .compressor import ZlibCompressor


def _test_compression():
    """Test compression and decompression functionality"""
    print("Testing compression functionality...")

    try:
        # Create compressor instance
        compressor = ZlibCompressor()

        # Test data
        test_data = "test123"
        print(f"Original data: {test_data}")

        # Test compression
        compressed = compressor.compress(test_data)
        print(f"Compressed size: {len(compressed)} bytes")

        # Test decompression
        decompressed = compressor.decompress(compressed)
        decompressed_text = decompressed.decode('utf-8')
        print(f"Decompressed data: {decompressed_text}")

        # Verify data integrity
        if test_data == decompressed_text:
            print("Compression test passed - data integrity verified")
        else:
            print("Compression test failed - data mismatch")
            return False

        # Save to file
        output_dir = r"C:\tmp"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "test.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Original: {test_data}\n")
            f.write(f"Decompressed: {decompressed_text}\n")
            f.write(f"Compression successful: {test_data == decompressed_text}\n")

        print(f"Test results saved to: {output_file}")

        # Additional file compression test
        test_file_path = os.path.join(output_dir, "test_original.txt")
        compressed_file_path = os.path.join(output_dir, "test_compressed.bin")
        decompressed_file_path = os.path.join(output_dir, "test_decompressed.txt")

        # Create test file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_data)

        # Test file compression
        compressor.compress_file(test_file_path, compressed_file_path)

        # Test file decompression
        compressor.decompress_file(compressed_file_path, decompressed_file_path)

        # Verify file content
        with open(decompressed_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read().strip()

        if test_data == file_content:
            print("File compression test passed")
        else:
            print("File compression test failed")
            return False

        print("All tests completed successfully!")
        return True

    except Exception as e:
        print(f"Test failed with error: {e}")
        return False