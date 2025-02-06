import json
from collections import defaultdict
import argparse
import sys
import re

class ValueAnalyzer:
    def __init__(self):
        self.findings = defaultdict(list)
        self.extension_pattern = re.compile(r'\.[a-zA-Z0-9]{2,4}$')
        
    def is_interesting(self, value):
        """Much simpler check - just look for long strings, paths, URLs, or files."""
        if not isinstance(value, str):
            return False
            
        value = str(value).strip()
        
        # Skip React/technical stuff
        if value.startswith('__') or value.startswith('[object'):
            return False
            
        # Capture any of these:
        return (len(value) > 50 or                    # Long strings
                '/' in value or                       # Paths
                '.' in value or                       # Possible files/extensions
                value.startswith(('http', '/api')))   # URLs
                
    def traverse(self, data, path=None):
        if path is None:
            path = []
            
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    if self.is_interesting(value):
                        self.findings[hash(value)].append({
                            'content': value,
                            'path': '/'.join(str(p) for p in path + [key])
                        })
                    self.traverse(value, path + [key])
                    
            elif isinstance(data, list):
                for i, value in enumerate(data):
                    if self.is_interesting(value):
                        self.findings[hash(value)].append({
                            'content': value,
                            'path': '/'.join(str(p) for p in path + [str(i)])
                        })
                    self.traverse(value, path + [str(i)])
                    
        except Exception:
            pass

    def print_findings(self):
        print("\nInteresting Content")
        print("=" * 50)
        
        # Group by frequency
        by_frequency = defaultdict(list)
        for _, occurrences in self.findings.items():
            by_frequency[len(occurrences)].append(occurrences)
            
        for count in sorted(by_frequency.keys(), reverse=True):
            for occurrences in by_frequency[count]:
                print(f"\nFound {count} times: {occurrences[0]['content']}")
                if count > 1:  # Only show paths if found multiple times
                    print("Locations:")
                    for loc in occurrences:
                        print(f"  - {loc['path']}")
                print()

def main():
    parser = argparse.ArgumentParser(description='Find interesting content in JSON')
    parser.add_argument('--input_file', help='Input JSON file to analyze')
    args = parser.parse_args()
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analyzer = ValueAnalyzer()
        analyzer.traverse(data)
        analyzer.print_findings()
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()