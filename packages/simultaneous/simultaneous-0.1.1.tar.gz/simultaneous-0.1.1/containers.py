"""Typed container provider identifiers for autocomplete-friendly usage."""

from enum import Enum


class Containers(str, Enum):
    E2B = "e2b"


# Backwards-compatible alias
E2B = Containers.E2B

