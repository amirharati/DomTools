#!/usr/bin/env python3
import json
import argparse
import sys

def compress_json(input_source, output_dest=None):
    """
    Compress JSON by removing whitespace and newlines.
    
    Args:
        input_source: File path or '-' for stdin
        output_dest: File path or None for stdout
    """
    try:
        # Read input
        if input_source == '-':
            data = json.load(sys.stdin)
        else:
            with open(input_source, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # Compress JSON
        compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        # Write output
        if output_dest:
            with open(output_dest, 'w', encoding='utf-8') as f:
                f.write(compressed)
        else:
            sys.stdout.write(compressed)
            sys.stdout.write('\n')  # Add newline for terminal friendliness
            
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: File operation failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Compress JSON by removing whitespace')
    parser.add_argument('input', help='Input JSON file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output file (defaults to stdout)')
    args = parser.parse_args()
    
    compress_json(args.input, args.output)

if __name__ == '__main__':
    main()