#!/usr/bin/env python3
import json
import argparse
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

class JSONObjectFinder:
    def __init__(self, search_keys: List[str]):
        self.search_keys = search_keys
        self.findings = defaultdict(list)
        
    def find_objects(self, obj: Any, path: List[str] = None) -> None:
        """Recursively find all instances of specified objects."""
        if path is None:
            path = []
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = path + [key]
                
                # If this is a key we're looking for, store the value
                if key in self.search_keys:
                    self.findings[key].append({
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
            instances = self.findings[key]
            if instances:
                print(f"\nFound {len(instances)} instance(s) of '{key}':")
                print("=" * 50)
                
                for i, instance in enumerate(instances, 1):
                    print(f"\nInstance {i}:")
                    print(f"Path: {instance['path']}")
                    print("Content:")
                    print(json.dumps(instance['value'], indent=2))
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