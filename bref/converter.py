import re
from typing import Dict, List, Tuple, Union, Any
from enum import Enum
from .parser import parse_type_definitions, find_type_annotation, parse_data_with_type

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
    import json
    
    # 1. BREF string'i parse et
    result = parse(bref_content)
    
    # 2. Python objesini JSON string'e çevir
    return json.dumps(result, ensure_ascii=False)


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
