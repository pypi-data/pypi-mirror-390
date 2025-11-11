"""Tests for TOON encoder."""
import pytest
from toon import encode


def test_encode_primitive_types():
    """Test encoding of primitive types."""
    # String
    assert encode({'name': 'Alice'}) == 'name: Alice'
    
    # Number
    assert encode({'age': 30}) == 'age: 30'
    assert encode({'price': 19.99}) == 'price: 19.99'
    
    # Boolean
    assert encode({'active': True}) == 'active: true'
    assert encode({'disabled': False}) == 'disabled: false'
    
    # Null
    assert encode({'value': None}) == 'value: null'


def test_encode_string_quoting():
    """Test string quoting rules."""
    # Simple string - no quotes
    assert encode({'name': 'Alice'}) == 'name: Alice'
    
    # String with comma - needs quotes
    assert encode({'text': 'Hello, World'}) == 'text: "Hello, World"'
    
    # String with colon - needs quotes
    assert encode({'text': 'key: value'}) == 'text: "key: value"'
    
    # String with leading/trailing space - needs quotes
    assert encode({'text': ' padded '}) == 'text: " padded "'
    
    # String that looks like boolean - needs quotes
    assert encode({'text': 'true'}) == 'text: "true"'
    assert encode({'text': 'false'}) == 'text: "false"'
    
    # String that looks like null - needs quotes
    assert encode({'text': 'null'}) == 'text: "null"'
    
    # Empty string - needs quotes
    assert encode({'text': ''}) == 'text: ""'


def test_encode_string_escaping():
    """Test string escaping."""
    # Quote escaping
    assert encode({'text': 'He said "hello"'}) == 'text: "He said \\"hello\\""'
    
    # Newline escaping
    assert encode({'text': 'line1\nline2'}) == 'text: "line1\\nline2"'
    
    # Backslash escaping
    assert encode({'text': 'path\\to\\file'}) == 'text: "path\\\\to\\\\file"'


def test_encode_empty_structures():
    """Test encoding of empty structures."""
    # Empty object
    assert encode({}) == '{}'
    
    # Empty array
    assert encode({'items': []}) == 'items: []'
    
    # Object with empty array
    data = {'data': {'items': []}}
    result = encode(data)
    assert 'data:' in result
    assert 'items: []' in result


def test_encode_primitive_array():
    """Test encoding of primitive arrays."""
    # Number array
    assert encode({'numbers': [1, 2, 3]}) == 'numbers: [1,2,3]'
    
    # String array
    assert encode({'names': ['Alice', 'Bob']}) == 'names: [Alice,Bob]'
    
    # Mixed primitive array
    assert encode({'mixed': [1, 'text', True, None]}) == 'mixed: [1,text,true,null]'
    
    # Array with quoted strings
    data = {'items': ['hello', 'world, test', 'foo']}
    result = encode(data)
    assert result == 'items: [hello,"world, test",foo]'


def test_encode_array_delimiter():
    """Test different array delimiters."""
    data = {'numbers': [1, 2, 3]}
    
    # Comma (default)
    assert encode(data, {'delimiter': 'comma'}) == 'numbers: [1,2,3]'
    
    # Tab
    result_tab = encode(data, {'delimiter': 'tab'})
    assert result_tab == 'numbers: [1\t2\t3]'
    
    # Pipe
    result_pipe = encode(data, {'delimiter': 'pipe'})
    assert result_pipe == 'numbers: [1|2|3]'


def test_encode_tabular_array():
    """Test encoding of uniform object arrays in tabular format."""
    data = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'}
        ]
    }
    
    result = encode(data)
    lines = result.split('\n')
    
    # Check header
    assert lines[0] == 'users[2]{id,name,role}:'
    
    # Check rows
    assert lines[1] == '  1,Alice,admin'
    assert lines[2] == '  2,Bob,user'


def test_encode_tabular_array_with_tab_delimiter():
    """Test tabular array with tab delimiter."""
    data = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    result = encode(data, {'delimiter': 'tab'})
    lines = result.split('\n')
    
    assert lines[0] == 'users[2]{id,name}:'
    assert lines[1] == '  1\tAlice'
    assert lines[2] == '  2\tBob'


def test_encode_non_uniform_array():
    """Test encoding of non-uniform arrays."""
    data = {
        'items': [
            {'id': 1, 'name': 'Item1'},
            {'id': 2, 'type': 'Special'}
        ]
    }
    
    result = encode(data)
    
    # Should use list format, not tabular
    assert 'items[2]:' in result
    assert '{' not in result  # No field header


def test_encode_nested_objects():
    """Test encoding of nested objects."""
    data = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    result = encode(data)
    lines = result.split('\n')
    
    # Check structure
    assert 'user:' in result
    assert 'name: Alice' in result
    assert 'profile:' in result
    assert 'age: 30' in result
    assert 'city: NYC' in result


def test_encode_key_folding():
    """Test key folding feature."""
    data = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    
    # Without key folding
    result_no_fold = encode(data, {'key_folding': 'off'})
    assert 'data:' in result_no_fold
    assert 'metadata:' in result_no_fold
    
    # With key folding
    result_fold = encode(data, {'key_folding': 'safe'})
    assert 'data.metadata.items' in result_fold


def test_encode_indentation():
    """Test custom indentation."""
    data = {
        'parent': {
            'child': 'value'
        }
    }
    
    # Default indent (2 spaces)
    result_default = encode(data)
    assert '  child: value' in result_default
    
    # Custom indent (4 spaces)
    result_custom = encode(data, {'indent': 4})
    assert '    child: value' in result_custom


def test_encode_special_float_values():
    """Test encoding of special float values (NaN, Infinity)."""
    import math
    
    # NaN
    assert encode({'value': float('nan')}) == 'value: null'
    
    # Infinity
    assert encode({'value': float('inf')}) == 'value: null'
    assert encode({'value': float('-inf')}) == 'value: null'


def test_encode_complex_structure():
    """Test encoding of complex nested structure."""
    data = {
        'project': 'TOON',
        'version': '1.0.0',
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ],
        'metadata': {
            'created': '2024-01-01',
            'tags': ['format', 'serialization', 'llm']
        }
    }
    
    result = encode(data)
    
    # Verify structure exists
    assert 'project: TOON' in result
    assert 'version: 1.0.0' in result
    assert 'users[2]{id,name,active}:' in result
    assert 'metadata:' in result
    assert 'tags: [format,serialization,llm]' in result
