# 🧬 BREF - Compact & Minimal Data Format

[![PyPI version](https://badge.fury.io/py/bref.svg)](https://badge.fury.io/py/bref)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/username/bref/graphs/commit-activity)

BREF is a compact, human-readable data format that supports type definitions, nested objects, arrays, and all JSON-compatible data types. This parser converts BREF strings into Python objects and provides a convenient CLI for JSON output.

## ✨ Features

- **🔧 Type Definitions** - Define schemas with `:type { field1, field2:type }`
- **🔄 Nested Objects** - Support for complex nested data structures
- **📋 Array Support** - Handle arrays with type annotations like `tracks:track[]`
- **🎯 Full JSON Compatibility** - Support for strings, numbers, booleans, null, objects, and arrays
- **⚡ Inline Schemas** - Define schemas inline with `: { field1, field2 }`
- **🚫 Missing Data Handling** - Skip fields with consecutive commas `,,`

## 🚀 Quick Start

### Installation

```bash
# From source
git clone https://github.com/yourusername/bref.git
cd bref
pip install -e .

# Development setup
pip install -e ".[dev]"
```

### Basic Usage

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

## 🖥️ Command Line Interface

The CLI automatically converts BREF to JSON:

```bash
# Parse file and output JSON
bref input.bref

# Pretty print JSON
bref input.bref --pretty

# Save to file
bref input.bref -o output.json

# Parse from stdin
echo ':song { title } { "Test Song" }: song' | bref
```

## 📚 Examples

See the `examples/` directory for more usage examples and test cases.

## 🛠️ Development

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

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for the BREF community**
