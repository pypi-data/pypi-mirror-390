"""TOON (Token-Oriented Object Notation) - A compact serialization format for LLMs."""

from .encoder import encode
from .decoder import decode
from .constants import (
    COMMA, TAB, PIPE,
    KEY_FOLDING_OFF, KEY_FOLDING_SAFE,
    EXPAND_PATHS_OFF, EXPAND_PATHS_SAFE
)

__version__ = '1.0.0'
__all__ = [
    'encode',
    'decode',
    'COMMA',
    'TAB',
    'PIPE',
    'KEY_FOLDING_OFF',
    'KEY_FOLDING_SAFE',
    'EXPAND_PATHS_OFF',
    'EXPAND_PATHS_SAFE',
]
