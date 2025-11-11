"""Basic usage examples for TOON format."""
from toon import encode, decode
import json


def example_simple_encoding():
    """Simple object encoding."""
    print("=== Simple Encoding ===")
    
    data = {
        'name': 'Alice',
        'age': 30,
        'active': True
    }
    
    toon = encode(data)
    print("Original:", json.dumps(data))
    print("\nTOON format:")
    print(toon)
    print()


def example_array_encoding():
    """Array encoding examples."""
    print("=== Array Encoding ===")
    
    # Primitive array
    data1 = {'numbers': [1, 2, 3, 4, 5]}
    print("Primitive array:")
    print(encode(data1))
    print()
    
    # Tabular array (uniform objects)
    data2 = {
        'users': [
            {'id': 1, 'name': 'Alice', 'role': 'admin'},
            {'id': 2, 'name': 'Bob', 'role': 'user'}
        ]
    }
    print("Tabular array:")
    print(encode(data2))
    print()


def example_nested_structure():
    """Nested structure encoding."""
    print("=== Nested Structure ===")
    
    data = {
        'project': 'TOON',
        'version': '1.0.0',
        'metadata': {
            'author': 'TOON Contributors',
            'created': '2024-01-01',
            'tags': ['serialization', 'llm', 'format']
        },
        'users': [
            {'id': 1, 'name': 'Alice', 'active': True},
            {'id': 2, 'name': 'Bob', 'active': False}
        ]
    }
    
    toon = encode(data)
    print("TOON format:")
    print(toon)
    print()


def example_decoding():
    """Decoding examples."""
    print("=== Decoding ===")
    
    toon = """users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user"""
    
    data = decode(toon)
    print("TOON input:")
    print(toon)
    print("\nDecoded to Python:")
    print(json.dumps(data, indent=2))
    print()


def example_round_trip():
    """Round-trip conversion."""
    print("=== Round-trip Conversion ===")
    
    original = {
        'items': [
            {'id': 1, 'name': 'Item 1', 'price': 19.99},
            {'id': 2, 'name': 'Item 2', 'price': 29.99}
        ]
    }
    
    print("Original:")
    print(json.dumps(original, indent=2))
    
    # Encode
    toon = encode(original)
    print("\nTOON format:")
    print(toon)
    
    # Decode
    result = decode(toon)
    print("\nDecoded back:")
    print(json.dumps(result, indent=2))
    
    # Verify
    print("\nRound-trip successful:", original == result)
    print()


if __name__ == '__main__':
    example_simple_encoding()
    example_array_encoding()
    example_nested_structure()
    example_decoding()
    example_round_trip()
