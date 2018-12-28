"""Utility functions"""
import sys

from typing import NoReturn


def log_fatal(err: str) -> NoReturn:
    print(err, file=sys.stderr)
    sys.exit(1)
