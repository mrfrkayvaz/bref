#!/usr/bin/env python3
"""
Command Line Interface for BREF parser
"""

import sys
import argparse
import json
from pathlib import Path
from .converter import parse, toJSON, toBREF


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
        "--format", 
        choices=["python", "json"], 
        default="python",
        help="Output format (default: python)"
    )
    parser.add_argument(
        "--pretty", 
        action="store_true",
        help="Pretty print output (for JSON format)"
    )
    
    args = parser.parse_args()
    
    try:
        # Read input
        if args.input:
            if Path(args.input).exists():
                # Input is a file
                with open(args.input, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Input is a string
                content = args.input
        else:
            # Read from stdin
            content = sys.stdin.read()
        
        # Parse BREF content
        result = parse(content)
        
        # Format output
        if args.format == "json":
            if args.pretty:
                output = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                output = json.dumps(result, ensure_ascii=False)
        else:
            # Python format
            output = repr(result)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
