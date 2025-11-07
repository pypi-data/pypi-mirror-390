import importlib.metadata

from .decode import decode
from .io import ASEIO, BytesIO
from .metadata import get_metadata
from .encode import encode

__all__ = ["encode", "decode", "BytesIO", "ASEIO", "get_metadata"]

__version__ = importlib.metadata.version("asebytes")
