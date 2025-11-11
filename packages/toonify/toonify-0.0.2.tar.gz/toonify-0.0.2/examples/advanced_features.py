"""Advanced features examples for TOON format."""
from toon import encode, decode
import json


def example_custom_delimiter():
    """Using different delimiters."""
    print("=== Custom Delimiters ===")
    
    data = {
        'users': [
            {'id': 1, 'name': 'Alice', 'dept': 'Engineering'},
            {'id': 2, 'name': 'Bob', 'dept': 'Sales'}
        ]
    }
    
    # Comma delimiter (default)
    print("Comma delimiter:")
    print(encode(data, {'delimiter': 'comma'}))
    print()
    
    # Tab delimiter
    print("Tab delimiter:")
    print(encode(data, {'delimiter': 'tab'}))
    print()
    
    # Pipe delimiter
    print("Pipe delimiter:")
    print(encode(data, {'delimiter': 'pipe'}))
    print()


def example_key_folding():
    """Key folding for deeply nested single-key objects."""
    print("=== Key Folding ===")
    
    data = {
        'response': {
            'data': {
                'user': {
                    'profile': {
                        'name': 'Alice'
                    }
                }
            }
        }
    }
    
    # Without key folding
    print("Without key folding:")
    print(encode(data, {'key_folding': 'off'}))
    print()
    
    # With key folding
    print("With key folding:")
    print(encode(data, {'key_folding': 'safe'}))
    print()


def example_path_expansion():
    """Path expansion during decoding."""
    print("=== Path Expansion ===")
    
    # TOON with dotted keys
    toon = 'user.profile.name: Alice\nuser.profile.age: 30'
    
    # Without expansion
    print("Without path expansion:")
    result_no_expand = decode(toon, {'expand_paths': 'off'})
    print(json.dumps(result_no_expand, indent=2))
    print()
    
    # With expansion
    print("With path expansion:")
    result_expand = decode(toon, {'expand_paths': 'safe'})
    print(json.dumps(result_expand, indent=2))
    print()


def example_custom_indentation():
    """Custom indentation size."""
    print("=== Custom Indentation ===")
    
    data = {
        'parent': {
            'child': {
                'value': 42
            }
        }
    }
    
    # 2 spaces (default)
    print("2-space indent:")
    print(encode(data, {'indent': 2}))
    print()
    
    # 4 spaces
    print("4-space indent:")
    print(encode(data, {'indent': 4}))
    print()


def example_special_characters():
    """Handling special characters."""
    print("=== Special Characters ===")
    
    data = {
        'message': 'Hello, World!',
        'path': 'C:\\Users\\Alice\\Documents',
        'quote': 'He said "hello"',
        'multiline': 'Line 1\nLine 2\nLine 3',
        'looks_like_bool': 'true'
    }
    
    toon = encode(data)
    print("Encoded:")
    print(toon)
    print()
    
    # Decode back
    result = decode(toon)
    print("Decoded:")
    print(json.dumps(result, indent=2))
    print()


def example_mixed_arrays():
    """Handling different array types."""
    print("=== Mixed Arrays ===")
    
    data = {
        'primitive_array': [1, 2, 3, 4, 5],
        'string_array': ['apple', 'banana', 'cherry'],
        'uniform_objects': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'mixed_objects': [
            {'id': 1, 'type': 'A'},
            {'id': 2, 'category': 'B'}  # Different fields
        ]
    }
    
    toon = encode(data)
    print("Encoded:")
    print(toon)
    print()


def example_empty_values():
    """Handling empty and null values."""
    print("=== Empty and Null Values ===")
    
    data = {
        'null_value': None,
        'empty_string': '',
        'empty_array': [],
        'empty_object': {},
        'nested_empty': {
            'inner': {}
        }
    }
    
    toon = encode(data)
    print("Encoded:")
    print(toon)
    print()
    
    result = decode(toon)
    print("Decoded:")
    print(json.dumps(result, indent=2))
    print()


def example_token_efficiency():
    """Compare token usage between JSON and TOON."""
    print("=== Token Efficiency ===")
    
    data = {
        'users': [
            {'id': 1, 'name': 'Alice Johnson', 'email': 'alice@example.com', 'active': True},
            {'id': 2, 'name': 'Bob Smith', 'email': 'bob@example.com', 'active': True},
            {'id': 3, 'name': 'Charlie Brown', 'email': 'charlie@example.com', 'active': False}
        ]
    }
    
    json_str = json.dumps(data, indent=2)
    toon_str = encode(data)
    
    print("JSON format:")
    print(json_str)
    print(f"\nJSON size: {len(json_str)} bytes")
    
    print("\nTOON format:")
    print(toon_str)
    print(f"\nTOON size: {len(toon_str)} bytes")
    
    reduction = (1 - len(toon_str) / len(json_str)) * 100
    print(f"\nSize reduction: {reduction:.1f}%")
    print()


if __name__ == '__main__':
    example_custom_delimiter()
    example_key_folding()
    example_path_expansion()
    example_custom_indentation()
    example_special_characters()
    example_mixed_arrays()
    example_empty_values()
    example_token_efficiency()
