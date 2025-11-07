"""Typed code interpreter provider identifiers for autocomplete-friendly usage."""

from enum import Enum


class CodeInterpreters(str, Enum):
    E2B = "e2b"


# Backwards-compatible alias
E2B = CodeInterpreters.E2B

