# BREF Python Parser

A Python parser for the BREF data format. BREF is a compact, human-readable data format that supports type definitions, nested objects, arrays, and all JSON-compatible data types.

## Features

- **Type Definitions**: Define schemas with `:type { field1, field2:type }`
- **Nested Objects**: Support for complex nested data structures
- **Array Support**: Handle arrays with type annotations like `tracks:track[]`
- **Full JSON Compatibility**: Support for strings, numbers, booleans, null, objects, and arrays
- **Inline Schemas**: Define schemas inline with `: { field1, field2 }`
- **Missing Data Handling**: Skip fields with consecutive commas `,,`

## Installation

### From Source

```bash
git clone https://github.com/yourusername/bref.git
cd bref
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Python API

```python
from bref import parse

# Parse BREF content
bref_content = """
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band, tracks:track[] }
:band { name, country }
:track { title }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" }, [{"track 1"}, {"track 2"}] },
    1980000000, true
  }
]: song
"""

result = parse(bref_content)
print(result)
```

### Command Line Interface

```bash
# Parse a file
bref input.bref

# Parse and output as JSON
bref input.bref --format json --pretty

# Parse and save to file
bref input.bref -o output.json --format json

# Parse from stdin
echo ':song { title } { "Test Song" }: song' | bref
```

## Examples

See the `examples/` directory for more usage examples.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black bref/
```

### Type Checking

```bash
mypy bref/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
