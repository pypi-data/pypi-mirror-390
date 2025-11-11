"""
storage.py
-----------

Binary bitmap storage for unique_random package.

Implements BinaryBitmapStorage, which provides a lightweight persistent bit-level
store for tracking used random numbers efficiently.

Author: Sai Rohith Pasupuleti
License: MIT
Minimum Python Version: 3.8+
"""

import os
import mmap


class BinaryBitmapStorage:
    """Persistent bitmap for tracking used numbers."""

    def __init__(self, start, end, filepath):
        self.start = start
        self.end = end
        self.filepath = str(filepath)
        self.size_bits = end - start + 1
        self.size_bytes = (self.size_bits + 7) // 8

        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        # Create or open existing file
        with open(self.filepath, "ab") as f:
            f.truncate(self.size_bytes)

        self.file = open(self.filepath, "r+b")
        self._mmap = mmap.mmap(self.file.fileno(), 0)
        self.used_count = 0

        # Count used bits at startup
        for byte in self._mmap:
            self.used_count += bin(byte).count("1")

    def _bit_indices(self, num):
        """Return byte index and bit mask for the given number."""
        offset = num - self.start
        return offset // 8, 1 << (offset % 8)

    def contains(self, num):
        """Check whether a number has already been marked as used."""
        byte_index, mask = self._bit_indices(num)
        return (self._mmap[byte_index] & mask) != 0

    def add(self, num):
        """Mark a number as used."""
        byte_index, mask = self._bit_indices(num)
        current_byte = self._mmap[byte_index]
        self._mmap[byte_index] = current_byte | mask
        self.used_count += 1

    def clear(self):
        """Reset all bits in the bitmap."""
        self._mmap.seek(0)
        self._mmap.write(b"\x00" * self.size_bytes)
        self._mmap.flush()
        self.used_count = 0

    def close(self):
        """Close the underlying memory map and file."""
        self._mmap.flush()
        self._mmap.close()
        self.file.close()
