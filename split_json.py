#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any, List
from copy import deepcopy

def get_chunk_size(data) -> int:
    """Get size in bytes of JSON data when serialized"""
    return len(json.dumps(data, separators=(',', ':')).encode())

class JSONSplitter:
    def __init__(self, output_dir: Path, max_size_bytes: int):
        self.output_dir = output_dir
        self.max_size = max_size_bytes
        self.chunk_num = 1

    def write_chunk(self, chunk: Dict[str, Any]):
        """Write a chunk of data to a file"""
        outfile = self.output_dir / f"chunk_{self.chunk_num}.json"
        with open(outfile, 'w') as f:
            json.dump(chunk, f, indent=2)
        size = get_chunk_size(chunk)
        print(f"Wrote chunk {self.chunk_num}: {size/1024/1024:.2f}MB")
        self.chunk_num += 1

    def needs_splitting(self, value: Any) -> bool:
        """Check if a value needs to be split"""
        if isinstance(value, (dict, list)):
            return get_chunk_size(value) > self.max_size
        elif isinstance(value, str):
            return len(value.encode()) > self.max_size
        return False

    def split_string(self, value: str) -> List[str]:
        """Split a string into chunks"""
        encoded = value.encode()
        chunks = []
        for i in range(0, len(encoded), self.max_size):
            chunk = encoded[i:i + self.max_size].decode(errors='ignore')
            chunks.append(chunk)
        return chunks

    def split_array(self, array: List[Any], base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split an array while maintaining the base structure"""
        chunks = []
        current_chunk = []
        
        for item in array:
            if isinstance(item, dict) and self.needs_splitting(item):
                # If we have accumulated items, create a chunk
                if current_chunk:
                    new_structure = deepcopy(base_structure)
                    new_structure['children'] = current_chunk
                    chunks.append(new_structure)
                    current_chunk = []
                
                # Process the large item
                item_chunks = self.split_dict(item)
                for item_chunk in item_chunks:
                    new_structure = deepcopy(base_structure)
                    new_structure['children'] = [item_chunk]
                    chunks.append(new_structure)
            else:
                current_chunk.append(item)
                
                # Check if current_chunk exceeds max size
                temp_structure = deepcopy(base_structure)
                temp_structure['children'] = current_chunk
                if get_chunk_size(temp_structure) > self.max_size:
                    # Remove last item and create chunk
                    current_chunk.pop()
                    new_structure = deepcopy(base_structure)
                    new_structure['children'] = current_chunk
                    chunks.append(new_structure)
                    current_chunk = [item]
        
        # Handle remaining items
        if current_chunk:
            new_structure = deepcopy(base_structure)
            new_structure['children'] = current_chunk
            chunks.append(new_structure)
        
        return chunks

    def split_dict(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a dictionary into chunks"""
        if not self.needs_splitting(data):
            return [data]

        base_structure = {}
        chunks = [deepcopy(data)]
        
        for key, value in data.items():
            if self.needs_splitting(value):
                if isinstance(value, str):
                    # Handle large string values
                    string_chunks = self.split_string(value)
                    new_chunks = []
                    for chunk in string_chunks:
                        for existing_chunk in chunks:
                            new_chunk = deepcopy(existing_chunk)
                            new_chunk[key] = chunk
                            new_chunks.append(new_chunk)
                    chunks = new_chunks
                
                elif isinstance(value, list):
                    # Handle arrays (especially for the children field)
                    if key == 'children':
                        base_structure = {k: v for k, v in data.items() if k != 'children'}
                        chunks = self.split_array(value, base_structure)
                
                elif isinstance(value, dict):
                    # Handle nested dictionaries
                    nested_chunks = self.split_dict(value)
                    if len(nested_chunks) > 1:
                        new_chunks = []
                        for nested_chunk in nested_chunks:
                            for existing_chunk in chunks:
                                new_chunk = deepcopy(existing_chunk)
                                new_chunk[key] = nested_chunk
                                new_chunks.append(new_chunk)
                        chunks = new_chunks

        return chunks

    def process(self, data: Dict[str, Any]):
        """Process the input data and write chunks"""
        chunks = self.split_dict(data)
        for chunk in chunks:
            self.write_chunk(chunk)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('--max-size', type=float, default=0.1,
                      help='Maximum size of each chunk in MB')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    with open(args.input) as f:
        data = json.load(f)
    
    max_bytes = int(args.max_size * 1024 * 1024)
    splitter = JSONSplitter(output_dir, max_bytes)
    splitter.process(data)

if __name__ == '__main__':
    main()