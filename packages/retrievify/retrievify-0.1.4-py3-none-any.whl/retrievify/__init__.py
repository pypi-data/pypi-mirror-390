# retrievify/__init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("retrievify")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .rag import RAG  # public API
