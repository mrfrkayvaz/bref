from .converter import parse, toJSON, toBREF, validate_bref

# Import Rust functions
try:
    from . import _bref
    read_bref_file = _bref.read_bref_file
    count_chars = _bref.count_chars
except ImportError:
    # Fallback if Rust module is not available
    def read_bref_file():
        raise ImportError("Rust module 'bref' not available. Please build the project with 'maturin develop' or 'maturin build'")
    
    def count_chars(s: str) -> int:
        raise ImportError("Rust module 'bref' not available. Please build the project with 'maturin develop' or 'maturin build'")

__all__ = ['parse', 'toJSON', 'toBREF', 'validate_bref', 'read_bref_file', 'count_chars']
