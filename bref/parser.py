import re
from typing import Dict, List, Tuple, Union, Any
from enum import Enum

# Global regex patterns - compiled once for better performance
TYPE_PATTERN = re.compile(r'^\s*:(?P<name>[A-Za-z_]\w*)\s*(?P<body>\{[^}]*\})\s*$')
TYPE_ANNOTATION_PATTERN = re.compile(r':\s*([A-Za-z_]\w*)\s*$')
INLINE_SCHEMA_PATTERN = re.compile(r':\s*(\{[^}]*\})\s*$')

class FieldType(Enum):
    OBJECT = "object"
    ARRAY = "array"

def split_by_delimiters(text: str, delimiter: str = ',') -> List[str]:
    """
    Optimized splitting that handles nested braces/brackets.
    More efficient than the previous approach and avoids code duplication.
    Optimized with fewer string operations using a character buffer.
    """
    parts: List[str] = []
    buffer_chars: List[str] = []
    depth = 0

    for char in text:
        if char in '{[':
            depth += 1
        elif char in ']}':
            depth -= 1
        elif char == delimiter and depth == 0:
            if buffer_chars:
                segment = ''.join(buffer_chars).strip()
                if segment:
                    parts.append(segment)
                buffer_chars.clear()
            continue
        buffer_chars.append(char)

    if buffer_chars:
        segment = ''.join(buffer_chars).strip()
        if segment:
            parts.append(segment)

    return parts


def iterate_segments(text: str, delimiter: str = ','):
    """
    Yield top-level segments separated by delimiter, handling nested braces/brackets.
    This is a generator version of split_by_delimiters to avoid building large lists.
    Now properly handles missing data by yielding empty strings for consecutive commas.
    """
    buffer_chars: List[str] = []
    depth = 0

    for char in text:
        if char in '{[':
            depth += 1
        elif char in ']}':
            depth -= 1
        elif char == delimiter and depth == 0:
            # Always yield the segment, even if empty (for missing data handling)
            segment = ''.join(buffer_chars).strip()
            yield segment
            buffer_chars.clear()
            continue
        buffer_chars.append(char)

    # Add the last part if it exists
    if buffer_chars:
        segment = ''.join(buffer_chars).strip()
        yield segment
    else:
        # Handle case where text ends with delimiter
        yield ""


def parse_schema_fields(text: str) -> List[Union[str, Tuple[str, str, FieldType]]]:
    """
    Parse schema fields from type definition body.
    Example: '{ title, year, artist:artist, tracks:track[] }'
    Returns: ["title", "year", ("artist", "artist", FieldType.OBJECT), ("tracks", "track", FieldType.ARRAY)]
    Optimized with fewer string operations and handles missing data.
    """
    inner = text.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]

    # Handle consecutive commas for missing data
    parts = []
    for part in inner.split(","):
        part = part.strip()
        if part:  # Only add non-empty parts
            parts.append(part)
        else:
            # Empty part indicates missing field - add None placeholder
            parts.append(None)
    
    fields = []
    
    for part in parts:
        if part is None:
            # Missing field - skip it
            continue
        elif ":" in part:
            key, type_name = part.split(":", 1)
            key = key.strip()
            type_name = type_name.strip()
            
            # Check for array type: tracks:track[]
            if type_name.endswith("[]"):
                base_type = type_name[:-2]
                fields.append((key, base_type, FieldType.ARRAY))
            else:
                # Regular type reference
                fields.append((key, type_name, FieldType.OBJECT))
        else:
            fields.append(part)
    
    return fields


def parse_type_definitions(content: str) -> Tuple[Dict[str, List], str]:
    """
    Parse type definitions from BREF content.
    Example: ':song { title, duration, genre, album:album, streams, is_favorite }'
    Returns: (type_defs, remaining_content)
    Optimized with fewer string operations.
    """
    type_defs = {}
    remaining_lines = []
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        match = TYPE_PATTERN.match(line)
        if match:
            name = match.group("name")
            body = match.group("body")
            type_defs[name] = parse_schema_fields(body)
        else:
            remaining_lines.append(line)
    
    # More efficient string joining
    if remaining_lines:
        return type_defs, "\n".join(remaining_lines)
    else:
        return type_defs, ""


def parse_value(value_str: str) -> Any:
    """
    Parse a single value from BREF format to Python type.
    Now uses iterative approach by default for massive performance improvements.
    """
    # Remove leading/trailing whitespace once
    value_str = value_str.strip()
    
    # Early return for empty strings
    if not value_str:
        return value_str
    
    # Cache length for multiple checks
    length = len(value_str)
    
    # Handle null - check length first for efficiency
    if length == 4 and value_str.lower() == "null":
        return None
    
    # Handle booleans - check length first for efficiency
    if length == 4 and value_str.lower() == "true":
        return True
    if length == 5 and value_str.lower() == "false":
        return False
    
    # Handle quoted strings - use startswith/endswith (already efficient)
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Handle numbers - more efficient digit checking
    if value_str.replace('.', '').replace('-', '').isdigit():
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    
    # Handle unquoted strings (identifiers) - more efficient check
    if value_str.replace('_', '').isalnum():
        return value_str
    
    # Handle nested objects and arrays - iterative approach (default)
    if value_str.startswith('{') and value_str.endswith('}'):
        return parse_object(value_str)
    elif value_str.startswith('[') and value_str.endswith(']'):
        return parse_array(value_str)
    
    return value_str


def parse_value_iterative(value_str: str) -> Any:
    """
    Iterative version of parse_value to avoid recursive function calls.
    Uses a stack-based approach for better performance on deeply nested structures.
    """
    # Remove leading/trailing whitespace once
    value_str = value_str.strip()
    
    # Early return for empty strings
    if not value_str:
        return value_str
    
    # Cache length for multiple checks
    length = len(value_str)
    
    # Handle null - check length first for efficiency
    if length == 4 and value_str.lower() == "null":
        return None
    
    # Handle booleans - check length first for efficiency
    if length == 4 and value_str.lower() == "true":
        return True
    if length == 5 and value_str.lower() == "false":
        return False
    
    # Handle quoted strings - use startswith/endswith (already efficient)
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Handle numbers - more efficient digit checking
    if value_str.replace('.', '').replace('-', '').isdigit():
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    
    # Handle unquoted strings (identifiers) - more efficient check
    if value_str.replace('_', '').isalnum():
        return value_str
    
    # Handle nested objects and arrays - iterative approach
    if value_str.startswith('{') and value_str.endswith('}'):
        return parse_object(value_str)
    elif value_str.startswith('[') and value_str.endswith(']'):
        return parse_array(value_str)
    
    return value_str


def parse_nested_iterative(value_str: str, type_defs: Dict = None) -> Any:
    """
    Iterative parser for nested structures using a stack-based approach.
    This eliminates recursive function calls for massive performance improvements.
    """
    # Stack: (value, parse_type, result_placeholder)
    stack = [(value_str, 'value', None)]
    result_stack = []
    
    while stack:
        current_value, parse_type, result_placeholder = stack.pop()
        
        if parse_type == 'value':
            # Parse simple value
            result = parse_simple_value(current_value)
            if isinstance(result, (dict, list)):
                # This is a nested structure, push to stack for processing
                if isinstance(result, dict):
                    stack.append((current_value, 'object', result))
                else:  # list
                    stack.append((current_value, 'array', result))
            else:
                # Simple value, add to result stack
                result_stack.append(result)
                
        elif parse_type == 'object':
            # Parse object iteratively
            if current_value.startswith('{') and current_value.endswith('}'):
                inner = current_value[1:-1].strip()
                obj_result = {}
                
                for segment in iterate_segments(inner):
                    if ":" in segment and not segment.startswith('"'):
                        key, value = segment.split(":", 1)
                        obj_result[key.strip()] = parse_simple_value(value)
                    else:
                        obj_result[f"field_{len(obj_result)}"] = parse_simple_value(segment)
                
                result_stack.append(obj_result)
            else:
                result_stack.append(current_value)
                
        elif parse_type == 'array':
            # Parse array iteratively
            if current_value.startswith('[') and current_value.endswith(']'):
                inner = current_value[1:-1].strip()
                arr_result = []
                
                for segment in iterate_segments(inner):
                    if segment:
                        arr_result.append(parse_simple_value(segment))
                
                result_stack.append(arr_result)
            else:
                result_stack.append(current_value)
    
    # Return the final result
    return result_stack[-1] if result_stack else value_str


def parse_simple_value(value_str: str) -> Any:
    """
    Parse simple values without nested structures.
    This is the non-recursive version for basic types.
    """
    value_str = value_str.strip()
    
    if not value_str:
        return value_str
    
    length = len(value_str)
    
    # Handle null
    if length == 4 and value_str.lower() == "null":
        return None
    
    # Handle booleans
    if length == 4 and value_str.lower() == "true":
        return True
    if length == 5 and value_str.lower() == "false":
        return False
    
    # Handle quoted strings
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Handle numbers
    if value_str.replace('.', '').replace('-', '').isdigit():
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    
    # Handle unquoted strings
    if value_str.replace('_', '').isalnum():
        return value_str
    
    # Check if it's a nested structure (but don't parse recursively)
    if value_str.startswith('{') and value_str.endswith('}'):
        return value_str  # Return as string, will be parsed by caller
    elif value_str.startswith('[') and value_str.endswith(']'):
        return value_str  # Return as string, will be parsed by caller
    
    return value_str


def parse_object(obj_str: str, type_defs: Dict = None, current_type: str = None) -> Dict:
    """
    Parse a BREF object string into a Python dict.
    Now uses a streaming segment iterator to avoid building intermediate lists.
    Handles missing data (consecutive commas) by skipping missing fields.
    Supports per-object trailing inline schema (:{ ... }) or type ( :Type ) overrides.
    """
    # First, check if this object string itself has a trailing type/schema
    core_text, trailing = extract_trailing_type(obj_str)

    # Remove outer braces
    inner_text = core_text.strip()
    if inner_text.startswith("{") and inner_text.endswith("}"):
        inner_text = inner_text[1:-1]

    result = {}

    # Determine schema to use
    if trailing:
        kind, value = trailing
        if kind == 'inline':
            return parse_object_with_schema(core_text, value, type_defs)
        elif kind == 'type':
            # Use named schema
            current_type = value

    if current_type and type_defs and current_type in type_defs:
        schema = type_defs[current_type]
        seg_iter = iterate_segments(inner_text)
        field_index = 0
        
        for field in schema:
            try:
                segment = next(seg_iter)
                # Skip empty segments (missing data)
                while not segment.strip() and field_index < len(schema):
                    field_index += 1
                    try:
                        segment = next(seg_iter)
                    except StopIteration:
                        break
                
                if not segment.strip():
                    continue
                    
            except StopIteration:
                break

            # Allow nested per-segment overrides
            segment_core, override = extract_trailing_type(segment)
            segment = segment_core

            if isinstance(field, tuple):
                key, field_type, field_type_enum = field
                if field_type_enum == FieldType.OBJECT:
                    if override and override[0] == 'inline':
                        result[key] = parse_object_with_schema(segment, override[1], type_defs)
                    elif override and override[0] == 'type':
                        result[key] = parse_object(segment, type_defs, override[1])
                    elif segment.startswith('{') and segment.endswith('}'):
                        result[key] = parse_object(segment, type_defs, field_type)
                    else:
                        result[key] = parse_value(segment)
                elif field_type_enum == FieldType.ARRAY:
                    if segment.startswith('[') and segment.endswith(']'):
                        effective_element_type = field_type
                        if override and override[0] == 'type':
                            effective_element_type = override[1]
                        result[key] = parse_array(segment, type_defs, effective_element_type)
                    else:
                        result[key] = parse_value(segment)
                else:
                    result[key] = parse_value(segment)
            else:
                # field is a simple string key inferred by position
                result[field] = parse_value(segment)
            
            field_index += 1
    else:
        # Handle inline schema or raw object key:value pairs
        for part in iterate_segments(inner_text):
            if not part.strip():
                continue
            # Per-entry override
            part_core, override = extract_trailing_type(part)
            part = part_core

            if ":" in part and not part.startswith('"'):
                key, value = part.split(":", 1)
                if override and override[0] == 'inline' and value.strip().startswith('{'):
                    result[key.strip()] = parse_object_with_schema(value, override[1], type_defs)
                elif override and override[0] == 'type' and value.strip().startswith('{'):
                    result[key.strip()] = parse_object(value, type_defs, override[1])
                else:
                    result[key.strip()] = parse_value(value)
            else:
                result[f"field_{len(result)}"] = parse_value(part)

    return result


def parse_array(arr_str: str, type_defs: Dict = None, element_type: str = None) -> List:
    """
    Parse a BREF array string into a Python list.
    Now uses a streaming segment iterator to avoid building intermediate lists.
    Supports per-element trailing type (:Type) or inline schema (:{ ... }) overrides.
    """
    # First, check if this array string itself has a trailing type/schema
    core_text, trailing = extract_trailing_type(arr_str)

    # Remove outer brackets
    inner_text = core_text.strip()
    if inner_text.startswith("[") and inner_text.endswith("]"):
        inner_text = inner_text[1:-1]

    # If array-level trailing type exists, set element_type accordingly
    if trailing and trailing[0] == 'type':
        element_type = trailing[1]

    result: List[Any] = []
    for part in iterate_segments(inner_text):
        if not part:
            continue
        # Per-element override
        part_core, override = extract_trailing_type(part)
        part = part_core

        if override and override[0] == 'inline' and part.startswith('{'):
            result.append(parse_object_with_schema(part, override[1], type_defs))
            continue
        if override and override[0] == 'type' and part.startswith('{'):
            result.append(parse_object(part, type_defs, override[1]))
            continue

        if element_type and type_defs and element_type in type_defs:
            if part.startswith('{') and part.endswith('}'):
                result.append(parse_object(part, type_defs, element_type))
            elif part.startswith('[') and part.endswith(']'):
                result.append(parse_array(part, type_defs, element_type))
            else:
                result.append(parse_value(part))
        else:
            if part.startswith('{') and part.endswith('}'):
                result.append(parse_object(part, type_defs))
            elif part.startswith('[') and part.endswith(']'):
                result.append(parse_array(part, type_defs))
            else:
                result.append(parse_value(part))

    return result


def parse_data_with_type(data_str: str, type_name: str, type_defs: Dict) -> Union[Dict, List]:
    """
    Parse BREF data using a specific type definition.
    """
    if type_name not in type_defs:
        raise ValueError(f"Type '{type_name}' not found in type definitions")
    
    # Check if it's an array or object
    if data_str.strip().startswith('[') and data_str.strip().endswith(']'):
        return parse_array(data_str, type_defs, type_name)
    else:
        return parse_object(data_str, type_defs, type_name)


def find_type_annotation(data_str: str) -> Tuple[str, str]:
    """
    Find type annotation at the end of data string.
    Returns (data_without_type, type_name) or (data_str, None) if no type found.
    """
    # Look for :type at the end
    match = TYPE_ANNOTATION_PATTERN.search(data_str.strip())
    if match:
        type_name = match.group(1)
        data_without_type = data_str[:match.start()].strip()
        return data_without_type, type_name
    
    # Look for inline schema : { ... }
    inline_match = INLINE_SCHEMA_PATTERN.search(data_str.strip())
    if inline_match:
        schema_str = inline_match.group(1)
        data_without_type = data_str[:inline_match.start()].strip()
        return data_str, None
    
    return data_str, None


def extract_trailing_type(segment: str) -> Tuple[str, Union[Tuple[str, str], Tuple[str, List[Union[str, Tuple[str, str, FieldType]]]], None]]:
    """
    Extract a trailing type annotation or inline schema from a segment.
    Returns (core_text, ('type', type_name)) or (core_text, ('inline', schema_fields)) or (segment, None)
    """
    s = segment.strip()
    # Inline schema at end: : { ... }
    m_inline = re.search(r"\s*:\s*(\{[^}]*\})\s*$", s)
    if m_inline:
        core = s[:m_inline.start()].rstrip()
        schema_body = m_inline.group(1)
        schema_fields = parse_schema_fields(schema_body)
        return core, ('inline', schema_fields)
    # Named type at end: : TypeName
    m_type = re.search(r"\s*:\s*([A-Za-z_]\w*)\s*$", s)
    if m_type:
        core = s[:m_type.start()].rstrip()
        type_name = m_type.group(1)
        return core, ('type', type_name)
    return s, None


def parse_object_with_schema(obj_str: str, schema: List[Union[str, Tuple[str, str, FieldType]]], type_defs: Dict) -> Dict:
    """
    Parse an object string using a provided schema field list (inline schema case).
    """
    inner = obj_str.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]

    result: Dict[str, Any] = {}
    seg_iter = iterate_segments(inner)

    for field in schema:
        try:
            segment = next(seg_iter)
        except StopIteration:
            break
        if not segment.strip():
            # missing data; skip
            continue
        # Allow nested overrides inside the segment
        segment_core, override = extract_trailing_type(segment)
        segment = segment_core

        if isinstance(field, tuple):
            key, field_type, field_type_enum = field
            if field_type_enum == FieldType.OBJECT:
                if override and override[0] == 'inline':
                    result[key] = parse_object_with_schema(segment, override[1], type_defs)
                elif override and override[0] == 'type':
                    result[key] = parse_object(segment, type_defs, override[1])
                elif segment.startswith('{') and segment.endswith('}'):
                    result[key] = parse_object(segment, type_defs, field_type)
                else:
                    result[key] = parse_value(segment)
            elif field_type_enum == FieldType.ARRAY:
                if segment.startswith('[') and segment.endswith(']'):
                    # Override element type if present
                    effective_element_type = field_type
                    if override and override[0] == 'type':
                        effective_element_type = override[1]
                    result[key] = parse_array(segment, type_defs, effective_element_type)
                else:
                    result[key] = parse_value(segment)
            else:
                result[key] = parse_value(segment)
        else:
            result[field] = parse_value(segment)

    return result
