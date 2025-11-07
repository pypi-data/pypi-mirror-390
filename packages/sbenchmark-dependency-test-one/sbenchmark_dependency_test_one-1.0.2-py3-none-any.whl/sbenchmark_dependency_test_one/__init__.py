"""
Python ≥3.12. Exposes name, version_number, version.
"""

__all__ = ["name", "version_number", "version", "__version__"]

__version__: str = "1.0.2"

def name() -> str:
    return "io.github.sbenchmark:python-dependency-1"

def version_number() -> str:
    return __version__

def version() -> str:
    return f"{name()},{version_number()}"
