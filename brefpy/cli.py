#!/usr/bin/env python3
"""
Command Line Interface for BREF parser
"""

import sys
import argparse
import json
from pathlib import Path
import brefpy


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Parse BREF format files and convert to Python objects or JSON"
    )
    parser.add_argument(
        "input", 
        nargs="?", 
        help="Input BREF file or string (if not provided, reads from stdin)"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file (if not provided, prints to stdout)"
    )
    parser.add_argument(
        "--pretty", 
        action="store_true",
        help="Pretty print JSON output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    try:
        # Read input
        if args.input:
            if Path(args.input).exists():
                # Input is a file
                if args.debug:
                    print(f"Reading file: {args.input}", file=sys.stderr)
                with open(args.input, 'r', encoding='utf-8') as f:
                    content = f.read()
                if args.debug:
                    print(f"File content length: {len(content)}", file=sys.stderr)
            else:
                # Input is a string
                content = args.input
                if args.debug:
                    print(f"Input string: {content}", file=sys.stderr)
        else:
            # Read from stdin
            content = sys.stdin.read()
            if args.debug:
                print("Reading from stdin", file=sys.stderr)
        
        if args.debug:
            print(f"Content to parse: {repr(content[:100])}...", file=sys.stderr)
        
        # Parse BREF content and convert to JSON
        result = brefpy.to_json(content)
        
        if args.pretty:
            # Parse the JSON string and pretty print it
            parsed_json = json.loads(result)
            output = json.dumps(parsed_json, indent=2, ensure_ascii=False)
        else:
            output = result
        
        if args.debug:
            print(f"Result: {result}", file=sys.stderr)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if args.debug:
                print(f"Output written to: {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
