"""
unique_random
-------------

A Python package for generating unique, non-repeating random numbers with
optional persistent storage using bitmap files.

Author: Sai Rohith Pasupuleti
License: MIT
Minimum Python Version: 3.8+
"""

__version__ = "1.0.0"
__author__ = "Sai Rohith Pasupuleti"


def about():
    """Return a short description of this package."""
    return (
        f"unique_random v{__version__}: Persistent, unique random number generator."
    )
