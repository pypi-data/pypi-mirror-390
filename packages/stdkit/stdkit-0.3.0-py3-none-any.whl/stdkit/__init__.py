__all__ = ["__version__", "chrono", "core", "exceptions", "rand"]

from importlib import metadata

from stdkit import chrono, core, exceptions, rand

__version__ = metadata.version(__name__)
