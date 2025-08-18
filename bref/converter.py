import re
from typing import Dict, List, Tuple, Union, Any
from enum import Enum


class FieldType(Enum):
    OBJECT = "object"
    ARRAY = "array"


def parse_schema_fields(text: str) -> List[Union[str, Tuple[str, str, FieldType]]]:
    """
    Parse schema fields from type definition body.
    Example: '{ title, year, artist:artist, tracks:track[] }'
    Returns: ["title", "year", ("artist", "artist", FieldType.OBJECT), ("tracks", "track", FieldType.ARRAY)]
    """
    inner = text.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]

    parts = [p.strip() for p in inner.split(",") if p.strip()]
    fields = []
    
    for part in parts:
        if ":" in part:
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
    """
    type_defs = {}
    remaining_lines = []
    
    # Type definition pattern: :name { field1, field2:type, ... }
    type_pattern = re.compile(r'^\s*:(?P<name>[A-Za-z_]\w*)\s*(?P<body>\{[^}]*\})\s*$')
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        match = type_pattern.match(line)
        if match:
            name = match.group("name")
            body = match.group("body")
            type_defs[name] = parse_schema_fields(body)
        else:
            remaining_lines.append(line)
    
    return type_defs, "\n".join(remaining_lines).strip()


def parse_value(value_str: str) -> Any:
    """
    Parse a single value from BREF format to Python type.
    """
    value_str = value_str.strip()
    
    # Handle null
    if value_str.lower() == "null":
        return None
    
    # Handle booleans
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    
    # Handle numbers
    if value_str.replace('.', '').replace('-', '').isdigit():
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    
    # Handle quoted strings
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Handle unquoted strings (identifiers)
    if value_str.replace('_', '').isalnum():
        return value_str
    
    # Handle nested objects and arrays
    if value_str.startswith('{') and value_str.endswith('}'):
        return parse_object(value_str)
    elif value_str.startswith('[') and value_str.endswith(']'):
        return parse_array(value_str)
    
    return value_str


def parse_object(obj_str: str, type_defs: Dict = None, current_type: str = None) -> Dict:
    """
    Parse a BREF object string into a Python dict.
    """
    # Remove outer braces
    inner = obj_str.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]
    
    # Split by commas, but handle nested braces and brackets
    parts = []
    current_part = ""
    brace_count = 0
    bracket_count = 0
    
    for char in inner:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        elif char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
        elif char == ',' and brace_count == 0 and bracket_count == 0:
            parts.append(current_part.strip())
            current_part = ""
            continue
        current_part += char
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    # Parse each part
    result = {}
    if current_type and current_type in type_defs:
        # Use type definition to map values to keys
        schema = type_defs[current_type]
        values = []
        
        # Parse each part with proper handling of nested objects/arrays
        for part in parts:
            if part.strip():
                if part.startswith('{') and part.endswith('}'):
                    # Nested object - need to find its type
                    values.append(part)
                elif part.startswith('[') and part.endswith(']'):
                    # Nested array - need to find its type
                    values.append(part)
                else:
                    # Simple value
                    values.append(parse_value(part))
        
        # Map values to schema fields
        for i, field in enumerate(schema):
            if i < len(values):
                if isinstance(field, tuple):
                    key, field_type, field_type_enum = field
                    if field_type_enum == FieldType.OBJECT:
                        # Parse nested object with its type definition
                        if isinstance(values[i], str) and values[i].startswith('{') and values[i].endswith('}'):
                            result[key] = parse_object(values[i], type_defs, field_type)
                        else:
                            result[key] = values[i]
                    elif field_type_enum == FieldType.ARRAY:
                        # Parse nested array with its element type
                        if isinstance(values[i], str) and values[i].startswith('[') and values[i].endswith(']'):
                            result[key] = parse_array(values[i], type_defs, field_type)
                        else:
                            result[key] = values[i]
                    else:
                        result[key] = values[i]
                else:
                    result[field] = values[i]
    else:
        # Handle inline schema or raw object
        for part in parts:
            if part.strip():
                if ":" in part and not part.startswith('"'):
                    # Key-value pair
                    key, value = part.split(":", 1)
                    result[key.strip()] = parse_value(value)
                else:
                    # Just a value
                    result[f"field_{len(result)}"] = parse_value(part)
    
    return result


def parse_array(arr_str: str, type_defs: Dict = None, element_type: str = None) -> List:
    """
    Parse a BREF array string into a Python list.
    """
    # Remove outer brackets
    inner = arr_str.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    
    # Split by commas, but handle nested braces
    parts = []
    current_part = ""
    brace_count = 0
    
    for char in inner:
        if char == '{' or char == '[':
            brace_count += 1
        elif char == '}' or char == ']':
            brace_count -= 1
        elif char == ',' and brace_count == 0:
            parts.append(current_part.strip())
            current_part = ""
            continue
        current_part += char
    
    if current_part.strip():
        parts.append(current_part.strip())
    
    # Parse each part
    result = []
    for part in parts:
        if part.strip():
            if element_type and element_type in type_defs:
                # Parse with type definition
                if part.startswith('{') and part.endswith('}'):
                    result.append(parse_object(part, type_defs, element_type))
                elif part.startswith('[') and part.endswith(']'):
                    result.append(parse_array(part, type_defs, element_type))
                else:
                    result.append(parse_value(part))
            else:
                # No element type specified, try to parse as best as possible
                if part.startswith('{') and part.endswith('}'):
                    # Try to parse as object without type definition
                    result.append(parse_object(part, type_defs))
                elif part.startswith('[') and part.endswith(']'):
                    # Try to parse as array without type definition
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
    match = re.search(r':\s*([A-Za-z_]\w*)\s*$', data_str.strip())
    if match:
        type_name = match.group(1)
        data_without_type = data_str[:match.start()].strip()
        return data_without_type, type_name
    
    # Look for inline schema : { ... }
    inline_match = re.search(r':\s*(\{[^}]*\})\s*$', data_str.strip())
    if inline_match:
        schema_str = inline_match.group(1)
        data_without_type = data_str[:inline_match.start()].strip()
        return data_str, None
    
    return data_str, None


def parse(bref_content: str) -> Union[dict, list]:
    """
    Parse BREF content into Python dict or list.
    
    Args:
        bref_content (str): BREF format string content
        
    Returns:
        Union[dict, list]: Parsed Python object (dict or list)
        
    Raises:
        ValueError: If type definition is missing or invalid
    """
    # Task 1: Parse type definitions first
    type_defs, data_text = parse_type_definitions(bref_content)
    
    # Task 2: Process the data using type_defs definitions
    if not data_text.strip():
        return {"type_defs": type_defs}
    
    # Find type annotation at the end of data
    data_without_type, type_name = find_type_annotation(data_text)
    
    if not type_name:
        raise ValueError("No type definition found for data. Data must have a type annotation (e.g., :song)")
    
    # Check if type is defined in type_defs
    if type_name not in type_defs:
        raise ValueError(f"Type '{type_name}' not found in type definitions")
    
    # Parse data using the type definition
    result = parse_data_with_type(data_without_type, type_name, type_defs)
    
    return result


def toJSON(bref_content: str) -> str:
    """
    Convert BREF format to JSON.
    
    Args:
        bref_content (str): BREF format string content
        
    Returns:
        JSON string (str)
    """
    pass


def toBREF(json_content: str) -> str:
    """
    Convert JSON to BREF format.
    
    Args:
        json_content (str): JSON content to convert
        
    Returns:
        str: BREF format string
    """
    # This function will remain empty for now as specified
    pass
