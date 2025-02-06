from collections import defaultdict
import json
import sys
import argparse

class DOMNodeAnalyzer:
    def __init__(self):
        self.key_stats = defaultdict(lambda: {
            'count': 0,
            'samples': []  # Will keep 3 sample values
        })
        self.max_samples = 3

    def traverse(self, data, path=None):
        if path is None:
            path = []
            
        try:
            if isinstance(data, dict):
                # Track each key we find
                for key, value in data.items():
                    stats = self.key_stats[key]
                    stats['count'] += 1
                    
                    # Keep up to 3 sample values
                    if len(stats['samples']) < self.max_samples:
                        sample = {
                            'value': value,
                            'path': '/'.join(str(p) for p in path + [key])
                        }
                        if sample not in stats['samples']:
                            stats['samples'].append(sample)
                            
                    # Continue traversing
                    self.traverse(value, path + [key])
                    
            elif isinstance(data, list):
                for i, value in enumerate(data):
                    self.traverse(value, path + [str(i)])
                    
        except Exception:
            pass

    def print_analysis(self):
        print("\nKey Analysis")
        print("=" * 50)
        
        # Sort by frequency
        sorted_keys = sorted(self.key_stats.items(), 
                           key=lambda x: (-x[1]['count'], x[0]))
        
        for key, stats in sorted_keys:
            print(f"\nKey: {key}")
            print(f"Count: {stats['count']}")
            if stats['samples']:
                print("Sample values:")
                for sample in stats['samples']:
                    print(f"  At {sample['path']}:")
                    print(f"  → {str(sample['value'])[:100]}")
                    if len(str(sample['value'])) > 100:
                        print("    ...")

def main():
    parser = argparse.ArgumentParser(description='Analyze JSON key usage')
    parser.add_argument('--input_file', help='Input JSON file to analyze')
    args = parser.parse_args()
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analyzer = DOMNodeAnalyzer()
        analyzer.traverse(data)
        analyzer.print_analysis()
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()