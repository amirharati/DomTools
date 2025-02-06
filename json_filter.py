#!/usr/bin/env python3
import json
import argparse
from typing import Dict, Any, Set
from pathlib import Path

class JSONFilter:
    def __init__(self, include_keys: Set[str]):
        self.include_keys = include_keys

    def filter_object(self, obj: Any) -> Any:
        """Filter object keeping entire subtrees of matched keys."""
        if isinstance(obj, dict):
            filtered = {}
            for key, value in obj.items():
                # If key is in our include set, keep the entire subtree
                if key in self.include_keys:
                    filtered[key] = value  # Keep the entire value without filtering
                else:
                    # Otherwise, continue filtering deeper
                    filtered_value = self.filter_object(value)
                    if filtered_value is not None:
                        filtered[key] = filtered_value
            return filtered if filtered else None
            
        elif isinstance(obj, list):
            filtered = [self.filter_object(item) for item in obj]
            filtered = [item for item in filtered if item is not None]
            return filtered if filtered else None
            
        return None

def load_keys_from_file(keys_file: Path) -> Set[str]:
    """Load keys from a text file, one key per line."""
    with open(keys_file, 'r') as f:
        # Strip whitespace and ignore empty lines
        return {line.strip() for line in f if line.strip()}

def main():
    parser = argparse.ArgumentParser(description='Filter JSON based on keys')
    parser.add_argument('input', type=Path, help='Input JSON file')
    parser.add_argument('keys', type=Path, help='Text file with keys to keep (one per line)')
    parser.add_argument('output', type=Path, help='Output JSON file')
    args = parser.parse_args()
    
    try:
        # Load input JSON
        with open(args.input, 'r') as f:
            data = json.load(f)
            
        # Load keys from file
        include_keys = load_keys_from_file(args.keys)
        print(f"Loaded {len(include_keys)} keys to keep: {', '.join(sorted(include_keys))}")
        
        # Create filter and process
        filter = JSONFilter(include_keys)
        filtered = filter.filter_object(data)
        
        # Write output
        with open(args.output, 'w') as f:
            json.dump(filtered, f, indent=2)
            
        print(f"Filtered JSON written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 