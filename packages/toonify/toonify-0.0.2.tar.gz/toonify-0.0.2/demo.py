#!/usr/bin/env python3
"""Demo script showcasing TOON format capabilities."""
import json
from toon import encode, decode

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_basic():
    """Basic encoding/decoding demo."""
    print_section("Basic TOON Encoding")
    
    data = {
        "name": "Alice",
        "age": 30,
        "city": "New York"
    }
    
    print("Python object:")
    print(json.dumps(data, indent=2))
    
    print("\nTOON format:")
    toon = encode(data)
    print(toon)
    
    print("\nDecoded back:")
    result = decode(toon)
    print(json.dumps(result, indent=2))

def demo_tabular():
    """Tabular array demo."""
    print_section("Tabular Arrays - The Power of TOON")
    
    data = {
        "users": [
            {"id": 1, "name": "Alice Smith", "role": "Engineer", "active": True},
            {"id": 2, "name": "Bob Jones", "role": "Designer", "active": True},
            {"id": 3, "name": "Carol White", "role": "Manager", "active": False}
        ]
    }
    
    json_str = json.dumps(data, indent=2)
    toon_str = encode(data)
    
    print("JSON format:")
    print(json_str)
    print(f"\nSize: {len(json_str)} bytes")
    
    print("\n" + "-"*60 + "\n")
    
    print("TOON format:")
    print(toon_str)
    print(f"\nSize: {len(toon_str)} bytes")
    
    reduction = (1 - len(toon_str) / len(json_str)) * 100
    print(f"\n✨ Size reduction: {reduction:.1f}%")

def demo_nested():
    """Nested structure demo."""
    print_section("Nested Structures")
    
    data = {
        "project": "TOON",
        "metadata": {
            "version": "1.0.0",
            "license": "MIT",
            "contributors": ["Alice", "Bob", "Carol"]
        }
    }
    
    toon = encode(data)
    print("TOON format:")
    print(toon)
    
    print("\nDecoded:")
    result = decode(toon)
    print(json.dumps(result, indent=2))

def demo_delimiters():
    """Different delimiter demo."""
    print_section("Custom Delimiters")
    
    data = {
        "items": [
            {"code": "A001", "name": "Widget", "price": 19.99},
            {"code": "B002", "name": "Gadget", "price": 29.99}
        ]
    }
    
    print("Tab delimiter (for spreadsheets):")
    toon_tab = encode(data, {"delimiter": "tab"})
    print(toon_tab)
    
    print("\nPipe delimiter (when data has commas):")
    toon_pipe = encode(data, {"delimiter": "pipe"})
    print(toon_pipe)

def demo_key_folding():
    """Key folding demo."""
    print_section("Key Folding for Deeply Nested Data")
    
    data = {
        "api": {
            "response": {
                "data": {
                    "user": {
                        "name": "Alice"
                    }
                }
            }
        }
    }
    
    print("Without key folding:")
    toon_normal = encode(data)
    print(toon_normal)
    
    print("\nWith key folding:")
    toon_folded = encode(data, {"key_folding": "safe"})
    print(toon_folded)
    
    print("\nWith path expansion on decode:")
    result = decode(toon_folded, {"expand_paths": "safe"})
    print(json.dumps(result, indent=2))

def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  TOON FORMAT LIBRARY - INTERACTIVE DEMO")
    print("  Token-Oriented Object Notation for LLMs")
    print("="*60)
    
    demo_basic()
    demo_tabular()
    demo_nested()
    demo_delimiters()
    demo_key_folding()
    
    print_section("Summary")
    print("✨ TOON achieves 30-60% size reduction vs JSON")
    print("✨ Perfect for LLM prompts and context windows")
    print("✨ Human-readable and easy to edit")
    print("✨ Fully reversible - no data loss")
    print("\nTry it yourself:")
    print("  pip install toon-format")
    print("  echo '{\"hello\": \"world\"}' | toon -e")
    print()

if __name__ == "__main__":
    main()
