#!/usr/bin/env python3
import json
import argparse
import sys

def process_json(input_source, output_dest=None, pretty=False):
    """
    Process JSON file - either compress or prettify it.
    
    Args:
        input_source: File path or '-' for stdin
        output_dest: File path or None for stdout
        pretty: If True, prettify. If False, compress
    """
    try:
        # Read input
        if input_source == '-':
            data = json.load(sys.stdin)
        else:
            with open(input_source, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # Process JSON
        if pretty:
            # Prettify with indentation and nice spacing
            processed = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
        else:
            # Compress by removing all unnecessary whitespace
            processed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        # Write output
        if output_dest:
            with open(output_dest, 'w', encoding='utf-8') as f:
                f.write(processed)
        else:
            sys.stdout.write(processed)
            sys.stdout.write('\n')
            
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: File operation failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Compress or prettify JSON')
    parser.add_argument('input', help='Input JSON file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output file (defaults to stdout)')
    #parser.add_argument('-p', '--pretty', action='store_true', 
    #                  help='Prettify JSON (default is to compress)')
    args = parser.parse_args()
    
    process_json(args.input, args.output, 'true')

if __name__ == '__main__':
    main()