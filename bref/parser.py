import re
from typing import Dict, List, Tuple, Union, Any


class FieldType:
    OBJECT = "object"
    ARRAY = "array"


def parse_value(value_str: str) -> Any:
    """
    Parse a single value from BREF format to Python type.
    Handles strings, numbers, booleans, null, and nested objects/arrays.
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
    
    # Split by commas, but handle nested braces
    parts = []
    current_part = ""
    brace_count = 0
    
    for char in inner:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        elif char == ',' and brace_count == 0:
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
        values = [parse_value(part) for part in parts if part.strip()]
        
        for i, field in enumerate(schema):
            if i < len(values):
                if isinstance(field, tuple):
                    key, field_type, field_type_enum = field
                    if field_type_enum == FieldType.OBJECT:
                        result[key] = values[i]
                    elif field_type_enum == FieldType.ARRAY:
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
                else:
                    result.append(parse_value(part))
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
