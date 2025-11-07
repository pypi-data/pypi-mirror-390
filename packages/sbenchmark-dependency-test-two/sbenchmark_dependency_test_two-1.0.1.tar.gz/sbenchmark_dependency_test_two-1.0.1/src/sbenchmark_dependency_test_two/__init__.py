"""
Python ≥3.12.
Depends on sbenchmark-dependency-test-one.
"""

from sbenchmark_dependency_test_one import version as deponeversion

__all__ = ["name", "version_number", "version", "dependency", "__version__"]

__version__: str = "1.0.1"


def name() -> str:
    return "io.github.sbenchmark:python-dependency-2"


def version_number() -> str:
    return __version__


def version() -> str:
    return f"{name()},{version_number()}"


def dependency() -> str:
    return deponeversion()
