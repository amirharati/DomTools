#!/usr/bin/env python3
import json
import argparse
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

class JSONObjectFinder:
    def __init__(self, search_keys: List[str]):
        self.search_keys = search_keys
        self.findings = defaultdict(lambda: defaultdict(list))
        
    def find_objects(self, obj: Any, path: List[str] = None) -> None:
        """Recursively find all instances of specified objects."""
        if path is None:
            path = []
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = path + [key]
                
                # If this is a key we're looking for, store the value
                if key in self.search_keys:
                    # Use JSON string as hash to identify identical objects
                    value_hash = json.dumps(value, sort_keys=True)
                    self.findings[key][value_hash].append({
                        'value': value,
                        'path': '/'.join(map(str, current_path))
                    })
                
                # Continue searching in this value
                self.find_objects(value, current_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self.find_objects(item, path + [str(i)])

    def print_findings(self):
        """Print findings in a structured format."""
        for key in self.search_keys:
            total_instances = sum(len(paths) for paths in self.findings[key].values())
            if total_instances:
                print(f"\nFound {total_instances} total instance(s) of '{key}':")
                print("=" * 50)
                
                # Print each unique value with its count
                for i, (_, instances) in enumerate(self.findings[key].items(), 1):
                    count = len(instances)
                    print(f"\nUnique Object {i} (found {count} time{'' if count == 1 else 's'}):")
                    print("Content:")
                    print(json.dumps(instances[0]['value'], indent=2))
                    if count > 1:
                        print("\nPaths:")
                        for instance in instances:
                            print(f"- {instance['path']}")
            else:
                print(f"\nNo instances of '{key}' found.")

def main():
    parser = argparse.ArgumentParser(description='Find specific objects in JSON')
    parser.add_argument('input', type=Path, help='Input JSON file')
    parser.add_argument('--objects', type=str, help='Comma-separated list of object names to find')
    args = parser.parse_args()
    
    try:
        # Parse the comma-separated list of objects
        search_keys = [key.strip() for key in args.objects.split(',')]
        print(f"Searching for objects: {', '.join(search_keys)}")
        
        # Load input JSON
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        # Create finder and process
        finder = JSONObjectFinder(search_keys)
        finder.find_objects(data)
        finder.print_findings()
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main() 