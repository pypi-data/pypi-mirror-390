"""Tests for TOON CLI."""
import sys
import json
import tempfile
from pathlib import Path
from io import StringIO
import pytest

from toon.cli import detect_mode, read_input, write_output, count_tokens


def test_detect_mode_from_extension():
    """Test mode detection from file extension."""
    # JSON file -> encode
    assert detect_mode('test.json', False, False) == 'encode'
    
    # TOON file -> decode
    assert detect_mode('test.toon', False, False) == 'decode'
    
    # Unknown extension -> encode (default)
    assert detect_mode('test.txt', False, False) == 'encode'


def test_detect_mode_with_flags():
    """Test mode detection with explicit flags."""
    # Force encode
    assert detect_mode('test.toon', True, False) == 'encode'
    
    # Force decode
    assert detect_mode('test.json', False, True) == 'decode'


def test_detect_mode_stdin():
    """Test mode detection for stdin."""
    # Stdin without flags -> encode (default)
    assert detect_mode('-', False, False) == 'encode'
    assert detect_mode(None, False, False) == 'encode'


def test_read_input_from_file():
    """Test reading input from file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write('{"test": "value"}')
        f.flush()
        temp_path = f.name
    
    try:
        content = read_input(temp_path)
        assert content == '{"test": "value"}'
    finally:
        Path(temp_path).unlink()


def test_write_output_to_file():
    """Test writing output to file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toon') as f:
        temp_path = f.name
    
    try:
        write_output('test: value', temp_path)
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        assert content == 'test: value'
    finally:
        Path(temp_path).unlink()


def test_count_tokens():
    """Test token counting (if tiktoken available)."""
    result = count_tokens('Hello, world!')
    
    # If tiktoken is available, should return int
    # Otherwise, should return None
    assert result is None or isinstance(result, int)
