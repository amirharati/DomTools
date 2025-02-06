#!/usr/bin/env python3
import json
import argparse
import re
from copy import deepcopy
from typing import Any, Dict, List, Tuple

PRUNE_PATTERNS = {
    'react_keys': [
        r'^__react',
        r'^_owner$',
        r'^_payload$',
        r'^_response$',
        r'^_chunks$',
        r'^_stringDecoder$',
        r'^\[object\s.*\]$'
    ],
    'feature_flag_keys': [
        'console_supported',
        'claudeai_supported',
        'phone_verification_supported',
        'stripe_address_supported',
        'mm_pdf'
    ],
    'technical_keys': [
        'rule_id',
        'group',
        'value',
        'name',  # When used with rule_id/group
        'props',
        'type',
        'index'
    ],
    'base64_looking_keys': [
        r'^[A-Za-z0-9+/]{20,}={0,2}$'  # Matches base64 encoded strings
    ],
    'style_classes': [
        r'^(flex|grid|text-|bg-|p-|m-|gap-|border-|rounded-|shadow-|transition-|overflow-)',
        r'(sm|md|lg|xl|2xl)$'
    ],
    'html_attributes': [
        {'height': '0'},
        {'width': '0'},
        {'display': 'none'},
        {'visibility': 'hidden'},
        'noscript',
        'iframe'
    ],
    'technical_metadata': [
        'undefined',
        'null',
        '[object Object]',
        '_owner',
        '__reactFiber',
        '__reactProps',
        'console_supported',
        'claudeai_supported', 
        'phone_verification_supported',
        'stripe_address_supported'
    ],
    'empty_technical': [
        {'props': {}},
        {'_chunks': {}},
        {'_stringDecoder': {}}
    ],
    'technical_values': [
        None, [], {}, '', False,  # Empty/null values
        'undefined',
        'null',
        '[object Object]',
        True,  # Boolean flags like console_supported=true
        0,     # Zero dimensions
        '0',   # String zero
        {}     # Empty objects
    ],
    'react_values': [
        r'^__react',
        r'^\[object\s.*\]$',
        r'^_[a-zA-Z]+'  # _owner, _payload, _chunks etc
    ],
    'base64_values': [
        r'^[A-Za-z0-9+/]{20,}={0,2}$'  # Those long base64 strings
    ]
}

# Common DOM text node values to prune
DOM_TEXT_VALUES = [
    '#text',
    '#comment',
    'fulfilled',
    '[object Object]',
    'UnserializableObject',
    '\n',
    'LINK',
    'default'
]

# CSS-related patterns - both for values and when these are keys
CSS_PATTERNS = {
    'keys': [
        'className',
        'style',
        'css',
        'tailwind'
    ],
    'values': [
        # Match common Tailwind/CSS class patterns
        r'^(mx|my|px|py|m|p|gap)-[0-9\.]+$',
        r'^flex(-[a-z]+)*$',
        r'^grid(-[a-z]+)*$',
        r'^(block|inline|hidden)$',
        r'^(mb|mt|ml|mr)-[0-9\.]+$',
        r'^space-(x|y)-[0-9\.]+$',
        r'^gap-[0-9\.]+$'
    ]
}

# Add at the top with other constants
REMOVE_KEYS = {
    'height',
    'width',
    'constructor',
    'fill',
    'viewBox'
}

class DOMPruner:
    def __init__(self, patterns: Dict = PRUNE_PATTERNS):
        self.patterns = patterns
        # Add CSS patterns to the main patterns
        self.patterns['css_values'] = CSS_PATTERNS['values']
        self.patterns['css_keys'] = CSS_PATTERNS['keys']
        self.compile_regex()

    def compile_regex(self):
        self.compiled_patterns = {
            category: [re.compile(pattern) if isinstance(pattern, str) else pattern
                      for pattern in patterns]
            for category, patterns in self.patterns.items()
            if category != 'css_keys'  # Don't compile simple key matches
        }

    def should_prune(self, value: Any, key: str = None) -> bool:
        # Never prune nodeName values
        if key == 'nodeName':
            return False
        
        # First check basic types
        if value is None or value == [] or value == {} or value == '':
            return True
        
        # Check exact string matches
        if isinstance(value, str):
            value = value.strip()
            
            # Check DOM text values
            if value in DOM_TEXT_VALUES:
                return True
            
            # Check string versions of null/undefined
            if value.lower() in ['null', 'undefined']:
                return True
            
            # Check CSS patterns if it looks like a class string
            if ' ' in value:  # Multiple classes
                classes = value.split()
                # If all classes match CSS patterns, prune it
                if all(any(pattern.match(cls) for pattern in self.compiled_patterns['css_values'])
                      for cls in classes):
                    return True
                
        # Prune booleans
        if isinstance(value, bool):
            return True
        
        # Prune simple numbers
        if isinstance(value, (int, float)):
            return True
        
        return False

    def prune_object(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            # Check if object has only nodeName property
            if list(obj.keys()) == ['nodeName']:
                return None
            
            pruned = {}
            for k, v in obj.items():
                # Skip keys we want to remove
                if k in REMOVE_KEYS:
                    continue
                
                # Skip if key matches CSS patterns
                if k in self.patterns['css_keys']:
                    continue
                
                pruned_value = self.prune_object(v)
                if pruned_value is not None:
                    pruned[k] = pruned_value
                
            if not pruned or all(self.should_prune(v, k) for k, v in pruned.items()):
                return None
            return pruned
        
        elif isinstance(obj, list):
            pruned = [self.prune_object(item) for item in obj 
                    if not self.should_prune(item)]
            # Return None if list is empty or only contains prunable values
            if not pruned or all(self.should_prune(item) for item in pruned):
                return None
            return pruned
        
        # For non-container values, only prune if explicitly matched
        if self.should_prune(obj):
            return None
        return obj

    def run_passes(self, data: Dict, max_passes: int = 10) -> Tuple[Dict, int]:
        previous = None
        current = deepcopy(data)
        passes = 0
        
        while passes < max_passes:
            previous = deepcopy(current)
            current = self.prune_object(current)
            
            if json.dumps(previous) == json.dumps(current):
                break
                
            passes += 1
        return current, passes

def main():
    parser = argparse.ArgumentParser(description='Prune DOM JSON data')
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('output', help='Output JSON file')
    parser.add_argument('--max-passes', type=int, default=1000)
    parser.add_argument('--patterns', type=str, help='JSON file with custom patterns')
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        patterns = PRUNE_PATTERNS
        if args.patterns:
            with open(args.patterns, 'r') as f:
                patterns = json.load(f)
        
        pruner = DOMPruner(patterns)
        pruned_data, num_passes = pruner.run_passes(data, args.max_passes)
        
        with open(args.output, 'w') as f:
            json.dump(pruned_data, f, indent=2)
            
        print(f"Completed in {num_passes} passes")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()