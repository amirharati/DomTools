# DOM Analysis Tools

A collection of command-line utilities for analyzing and manipulating DOM data in JSON format. These tools help find specific objects in JSON structures, filter JSON based on keys, clean up React/DOM data, split large JSON files, and analyze JSON values. The tools are particularly useful when working with complex nested JSON structures like React component trees and chat message data.

## Available Tools and Usage

### dumpDOM.js
Browser console utility to capture complete DOM snapshots.
```javascript
// In browser console:
dumpDOM()  // Captures full DOM
dumpDOM(maxDepth)  // Capture with depth limit

// Outputs: dom-snapshot-{timestamp}.json
```

### json_object_finder.py
Lists all instances of specified objects in a JSON file, showing their full path and content.
```bash
python json_object_finder.py input.json --objects "message,content"
# Example: Find all message and content objects in input.json
```

### json_filter.py  
Keeps only specified keys and their entire subtrees, removing everything else.
```bash
python json_filter.py input.json keys.txt output.json
# keys.txt: one key per line to keep
```

### compress_json.py
Compresses JSON by removing whitespace and formatting.
```bash
python compress_json.py input.json -o output.json
python compress_json.py input.json  # outputs to stdout
python compress_json.py - -o output.json  # read from stdin
```

### decompress_json.py
Makes JSON human-readable with proper formatting and indentation.
```bash
python decompress_json.py input.json -o output.json
python decompress_json.py input.json  # outputs to stdout
python decompress_json.py - -o output.json  # read from stdin
```

### dom_pruner.py
Cleans DOM/React JSON by removing technical metadata and React-specific properties.
```bash
python dom_pruner.py input.json output.json
```

### split_json.py
Breaks large JSON files into smaller manageable chunks.
```bash
python split_json.py input.json output_dir --max-size 0.1
# max-size in MB
```

### value_analyzer.py
Finds patterns and interesting values in JSON data.
```bash
python value_analyzer.py --input_file input.json
```

## Requirements
- Python 3.6+ (for Python tools)
- Modern web browser (for dumpDOM.js)
- No external dependencies

## Workflow Example
1. Capture DOM snapshot in browser:
```javascript
dumpDOM()  // Creates dom-snapshot-{timestamp}.json
```

2. Clean and analyze the snapshot:
```bash
# Clean up the snapshot
python dom_pruner.py dom-snapshot-1234567890.json cleaned.json

# Compress for storage
python compress_json.py cleaned.json -o compressed.json

# Later, decompress for analysis
python decompress_json.py compressed.json -o readable.json

# Find specific objects
python json_object_finder.py readable.json --objects "message"
```

## Note
All tools are standalone and can be used independently or in combination. The Python tools work with any JSON data, while dumpDOM.js is specifically for capturing browser DOM structures.
