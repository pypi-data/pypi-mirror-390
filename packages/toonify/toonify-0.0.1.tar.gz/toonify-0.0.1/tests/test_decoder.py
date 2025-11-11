"""Tests for TOON decoder."""
import pytest
from toon import decode


def test_decode_primitive_types():
    """Test decoding of primitive types."""
    # String
    assert decode('name: Alice') == {'name': 'Alice'}
    
    # Number
    assert decode('age: 30') == {'age': 30}
    assert decode('price: 19.99') == {'price': 19.99}
    
    # Boolean
    assert decode('active: true') == {'active': True}
    assert decode('disabled: false') == {'disabled': False}
    
    # Null
    assert decode('value: null') == {'value': None}


def test_decode_quoted_strings():
    """Test decoding of quoted strings."""
    # Simple quoted string
    assert decode('name: "Alice"') == {'name': 'Alice'}
    
    # String with comma
    assert decode('text: "Hello, World"') == {'text': 'Hello, World'}
    
    # String with colon
    assert decode('text: "key: value"') == {'text': 'key: value'}
    
    # String with spaces
    assert decode('text: " padded "') == {'text': ' padded '}
    
    # Empty string
    assert decode('text: ""') == {'text': ''}


def test_decode_escaped_strings():
    """Test decoding of escaped strings."""
    # Escaped quotes
    assert decode('text: "He said \\"hello\\""') == {'text': 'He said "hello"'}
    
    # Escaped newline
    assert decode('text: "line1\\nline2"') == {'text': 'line1\nline2'}
    
    # Escaped backslash
    assert decode('text: "path\\\\to\\\\file"') == {'text': 'path\\to\\file'}
    
    # Escaped tab
    assert decode('text: "col1\\tcol2"') == {'text': 'col1\tcol2'}


def test_decode_empty_structures():
    """Test decoding of empty structures."""
    # Empty object
    result = decode('data: {}')
    assert result == {'data': {}}
    
    # Empty array
    assert decode('items: []') == {'items': []}


def test_decode_primitive_array():
    """Test decoding of primitive arrays."""
    # Number array
    assert decode('numbers: [1,2,3]') == {'numbers': [1, 2, 3]}
    
    # String array
    assert decode('names: [Alice,Bob]') == {'names': ['Alice', 'Bob']}
    
    # Mixed array
    assert decode('mixed: [1,text,true,null]') == {'mixed': [1, 'text', True, None]}
    
    # Array with quoted strings
    result = decode('items: [hello,"world, test",foo]')
    assert result == {'items': ['hello', 'world, test', 'foo']}


def test_decode_array_delimiters():
    """Test decoding with different delimiters."""
    # Tab delimiter
    assert decode('numbers: [1\t2\t3]') == {'numbers': [1, 2, 3]}
    
    # Pipe delimiter
    assert decode('numbers: [1|2|3]') == {'numbers': [1, 2, 3]}


def test_decode_tabular_array():
    """Test decoding of tabular arrays."""
    toon = """users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user"""
    
    result = decode(toon)
    
    expected = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'}
        ]
    }
    
    assert result == expected


def test_decode_tabular_array_with_tab():
    """Test decoding tabular array with tab delimiter."""
    toon = """users[2]{id,name}:
  1\tAlice
  2\tBob"""
    
    result = decode(toon)
    
    expected = {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ]
    }
    
    assert result == expected


def test_decode_list_array():
    """Test decoding of list arrays."""
    toon = """items[3]:
  value1
  value2
  value3"""
    
    result = decode(toon)
    assert result == {'items': ['value1', 'value2', 'value3']}


def test_decode_nested_objects():
    """Test decoding of nested objects."""
    toon = """user:
  name: Alice
  profile:
    age: 30
    city: NYC"""
    
    result = decode(toon)
    
    expected = {
        'user': {
            'name': 'Alice',
            'profile': {
                'age': 30,
                'city': 'NYC'
            }
        }
    }
    
    assert result == expected


def test_decode_path_expansion():
    """Test path expansion feature."""
    toon = 'data.metadata.items: [1,2,3]'
    
    # Without expansion
    result_no_expand = decode(toon, {'expand_paths': 'off'})
    assert result_no_expand == {'data.metadata.items': [1, 2, 3]}
    
    # With expansion
    result_expand = decode(toon, {'expand_paths': 'safe'})
    expected = {
        'data': {
            'metadata': {
                'items': [1, 2, 3]
            }
        }
    }
    assert result_expand == expected


def test_decode_complex_structure():
    """Test decoding of complex structure."""
    toon = """project: TOON
version: 1.0.0
users[2]{id,name,active}:
  1,Alice,true
  2,Bob,false
metadata:
  created: 2024-01-01
  tags: [format,serialization,llm]"""
    
    result = decode(toon)
    
    expected = {
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
    
    assert result == expected


def test_decode_empty_lines():
    """Test decoding with empty lines."""
    toon = """name: Alice

age: 30

active: true"""
    
    result = decode(toon)
    assert result == {'name': 'Alice', 'age': 30, 'active': True}


def test_decode_number_formats():
    """Test decoding various number formats."""
    toon = """int: 42
float: 3.14
negative: -10
scientific: 1.5e10"""
    
    result = decode(toon)
    
    assert result['int'] == 42
    assert result['float'] == 3.14
    assert result['negative'] == -10
    assert result['scientific'] == 1.5e10


def test_decode_quoted_field_values():
    """Test decoding with quoted values in tabular arrays."""
    toon = """items[2]{id,description}:
  1,"Item with, comma"
  2,"Normal item\""""
    
    result = decode(toon)
    
    expected = {
        'items': [
            {'id': 1, 'description': 'Item with, comma'},
            {'id': 2, 'description': 'Normal item'}
        ]
    }
    
    assert result == expected
