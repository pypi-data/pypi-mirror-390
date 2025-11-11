"""
core.py
-------

Core logic for the unique_random package.

Implements the UniqueRandom class, which provides non-repeating random numbers
over a defined range. Optionally supports persistent state across runs using
binary bitmap storage.

Author: Sai Rohith Pasupuleti
License: MIT
Minimum Python Version: 3.8+
"""

import os
import random
from pathlib import Path
from .storage import BinaryBitmapStorage


class UniqueRandom:
    """
    Generate unique random integers within a range, with optional persistence.

    Parameters
    ----------
    start : int
        Starting integer of the range (inclusive).
    end : int
        Ending integer of the range (inclusive).
    persistent : bool, optional
        Whether to persist state in a bitmap file between runs.
    on_exhaust : {'error', 'reset', 'repeat'}, optional
        Behavior when all numbers are used.
        - 'error': raise an exception.
        - 'reset': reset state automatically.
        - 'repeat': start reusing numbers after exhaustion.
    """

    def __init__(self, start, end, persistent=False, on_exhaust="error"):
        if start > end:
            raise ValueError("Start value cannot be greater than end value.")

        self.start = start
        self.end = end
        self.persistent = persistent
        self.on_exhaust = on_exhaust

        # Local set for non-persistent mode
        self._used = set()

        # Create persistent bitmap store if enabled
        if self.persistent:
            home = Path.home() / ".unique_random"
            home.mkdir(exist_ok=True)
            filename = f"state_{self.start}_{self.end}.bin"
            filepath = home / filename
            self._persistent_store = BinaryBitmapStorage(self.start, self.end, filepath)
        else:
            self._persistent_store = None

    def randint(self):
        """
        Return a unique random integer between start and end (inclusive).

        Handles duplicate avoidance using in-memory or persistent bitmap tracking.
        """
        while True:
            num = random.randint(self.start, self.end)
            already_used = (
                num in self._used
                if not self.persistent
                else self._persistent_store.contains(num)
            )

            if not already_used or self.on_exhaust == "repeat":
                if self.persistent:
                    self._persistent_store.add(num)
                else:
                    self._used.add(num)
                return num

            # Handle exhaustion conditions
            if self.on_exhaust == "reset":
                self.reset()
            elif self.on_exhaust == "error":
                total = self.end - self.start + 1
                used = (
                    len(self._used)
                    if not self.persistent
                    else "unknown (bitmap persistence)"
                )
                raise RuntimeError(f"All {total} numbers have been used (used={used}).")

    def reset(self):
        """Reset the internal or persistent state."""
        if self.persistent and self._persistent_store:
            self._persistent_store.clear()
        self._used.clear()

    def stats(self):
        """Return a dictionary with current generator statistics."""
        return {
            "range": (self.start, self.end),
            "persistent": self.persistent,
            "on_exhaust": self.on_exhaust,
            "used_count": len(self._used)
            if not self.persistent
            else "bitmap persistence active",
            "total": self.end - self.start + 1,
            "file": str(self._persistent_store.filepath)
            if self.persistent
            else None,
        }

    def close(self):
        """Close the persistent store if applicable."""
        if self._persistent_store:
            self._persistent_store.close()
