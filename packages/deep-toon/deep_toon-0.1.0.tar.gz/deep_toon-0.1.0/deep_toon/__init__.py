"""
Deep-TOON: Deep Token-Oriented Object Notation

Lightweight JSON compression for LLM applications.

Example:
    >>> from deep_toon import encode, decode
    >>> data = {"users": [{"name": "Alice", "age": 30}]}
    >>> compressed = encode(data)
    >>> original = decode(compressed)
"""

__version__ = "0.1.0"

from .encoder import DeepToonEncoder
from .decoder import DeepToonDecoder, DeepToonDecodeError

# Simple API
def encode(data):
    """Encode JSON data to Deep-TOON format."""
    return DeepToonEncoder().encode(data)

def decode(deep_toon_str):
    """Decode Deep-TOON format back to JSON."""
    return DeepToonDecoder().decode(deep_toon_str)

__all__ = ["encode", "decode", "DeepToonEncoder", "DeepToonDecoder", "DeepToonDecodeError"]