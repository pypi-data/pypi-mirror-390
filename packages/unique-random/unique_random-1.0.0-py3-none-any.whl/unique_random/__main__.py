"""
__main__.py
------------

Command-line interface (CLI) for the unique_random package.

This module allows users to interact with the UniqueRandom generator directly
from the terminal. It supports generating random numbers, resetting the state,
and checking generator statistics.

Usage examples
--------------
    $ python -m unique_random --generate 5 --start 1 --end 100
    $ python -m unique_random --stats --start 1 --end 100
    $ python -m unique_random --reset --start 1 --end 100

Author: Sai Rohith Pasupuleti
License: MIT
Minimum Python Version: 3.8+
"""

import argparse
from .core import UniqueRandom


def main():
    """Parse command-line arguments and execute the requested operation."""
    parser = argparse.ArgumentParser(
        description="unique_random - Generate unique random numbers with optional persistence."
    )

    parser.add_argument("--generate", type=int, help="Number of random values to generate.")
    parser.add_argument("--start", type=int, required=True, help="Start of the random range.")
    parser.add_argument("--end", type=int, required=True, help="End of the random range.")
    parser.add_argument("--reset", action="store_true", help="Reset the generator state.")
    parser.add_argument("--stats", action="store_true", help="Display generator statistics.")
    parser.add_argument(
        "--persistent",
        action="store_true",
        help="Enable persistent bitmap storage across runs.",
    )
    parser.add_argument(
        "--on-exhaust",
        choices=["error", "reset", "repeat"],
        default="error",
        help="Behavior when all numbers have been used. Default: error",
    )

    args = parser.parse_args()

    ur = UniqueRandom(
        args.start,
        args.end,
        persistent=args.persistent,
        on_exhaust=args.on_exhaust,
    )

    # Handle the --generate option
    if args.generate:
        print(f"Generating {args.generate} unique numbers:")
        try:
            for _ in range(args.generate):
                print(ur.randint())
        except RuntimeError as exc:
            print(f"Error: {exc}")

    # Handle --stats option
    elif args.stats:
        print("Current generator state:\n")
        for key, value in ur.stats().items():
            print(f"  {key:>12}: {value}")

    # Handle --reset option
    elif args.reset:
        ur.reset()
        print("State reset successfully.")

    # Default behavior: show help if no arguments are given
    else:
        parser.print_help()

    ur.close()


if __name__ == "__main__":
    main()
