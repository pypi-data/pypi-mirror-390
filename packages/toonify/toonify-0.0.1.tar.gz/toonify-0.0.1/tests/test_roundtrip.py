"""Tests for round-trip encoding and decoding."""
import pytest
from toon import encode, decode


def test_roundtrip_simple_object():
    """Test round-trip of simple object."""
    original = {
        'name': 'Alice',
        'age': 30,
        'active': True
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_nested_object():
    """Test round-trip of nested object."""
    original = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_primitive_array():
    """Test round-trip of primitive arrays."""
    original = {
        'numbers': [1, 2, 3, 4, 5],
        'names': ['Alice', 'Bob', 'Charlie'],
        'mixed': [1, 'text', True, None]
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_tabular_array():
    """Test round-trip of tabular array."""
    original = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'},
            {'id': 3, 'name': 'Charlie', 'role': 'guest'}
        ]
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_empty_structures():
    """Test round-trip of empty structures."""
    original = {
        'empty_object': {},
        'empty_array': [],
        'nested': {
            'also_empty': {}
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_special_strings():
    """Test round-trip of strings requiring quotes."""
    original = {
        'comma': 'hello, world',
        'colon': 'key: value',
        'quote': 'He said "hello"',
        'newline': 'line1\nline2',
        'spaces': '  padded  ',
        'looks_like_bool': 'true',
        'looks_like_null': 'null'
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_complex_structure():
    """Test round-trip of complex structure."""
    original = {
        'project': 'TOON',
        'version': '1.0.0',
        'description': 'A token-efficient format',
        'features': ['compact', 'readable', 'structured'],
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ],
        'metadata': {
            'created': '2024-01-01',
            'author': 'TOON Contributors',
            'stats': {
                'files': 10,
                'lines': 1000
            }
        }
    }
    
    toon = encode(original)
    result = decode(toon)
    
    assert result == original


def test_roundtrip_with_delimiters():
    """Test round-trip with different delimiters."""
    original = {
        'values': [1, 2, 3],
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    # Tab delimiter
    toon_tab = encode(original, {'delimiter': 'tab'})
    result_tab = decode(toon_tab)
    assert result_tab == original
    
    # Pipe delimiter
    toon_pipe = encode(original, {'delimiter': 'pipe'})
    result_pipe = decode(toon_pipe)
    assert result_pipe == original


def test_roundtrip_key_folding_and_expansion():
    """Test round-trip with key folding and path expansion."""
    original = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    
    # Encode with key folding
    toon = encode(original, {'key_folding': 'safe'})
    
    # Decode with path expansion
    result = decode(toon, {'expand_paths': 'safe'})
    
    assert result == original


def test_roundtrip_multiple_iterations():
    """Test multiple encode-decode cycles maintain consistency."""
    original = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'count': 2
    }
    
    # First cycle
    toon1 = encode(original)
    result1 = decode(toon1)
    
    # Second cycle
    toon2 = encode(result1)
    result2 = decode(toon2)
    
    # Third cycle
    toon3 = encode(result2)
    result3 = decode(toon3)
    
    # All should be equal
    assert result1 == original
    assert result2 == original
    assert result3 == original
    assert toon1 == toon2 == toon3
