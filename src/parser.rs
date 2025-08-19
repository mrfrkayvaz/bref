use std::collections::HashMap;
use crate::types::{FieldKind, FieldDef, TypeDefs, DataValue, PrimitiveValue};
use crate::utils::{find_simple_colon, check_if_all_key_value_pairs, find_main_colon, parse_primitive_value};

/// Parse type definitions from Bref format
pub fn parse_type_definitions(input: &str) -> TypeDefs {
    let mut type_defs = HashMap::new();
    
    for line in input.lines() {
        let line = line.trim();
        
        if line.is_empty() {
            continue;
        }
        
        if line.starts_with(':') {
            if let Some(type_def) = parse_type_definition(line) {
                type_defs.insert(type_def.0, type_def.1);
            }
        }
    }
    
    type_defs
}

/// Parse a single type definition line
fn parse_type_definition(line: &str) -> Option<(String, Vec<FieldDef>)> {
    let line = &line[1..];
    
    if let Some(space_pos) = line.find(' ') {
        let type_name = line[..space_pos].trim().to_string();
        let fields_part = line[space_pos..].trim();
        
        if fields_part.starts_with('{') && fields_part.ends_with('}') {
            let fields_content = &fields_part[1..fields_part.len()-1];
            let fields = parse_fields(fields_content);
            return Some((type_name, fields));
        }
    }
    
    None
}

/// Parse field definitions from a comma-separated string
fn parse_fields(fields_content: &str) -> Vec<FieldDef> {
    let mut fields = Vec::new();
    
    for field_str in fields_content.split(',') {
        let field_str = field_str.trim();
        if !field_str.is_empty() {
            if let Some(field_def) = parse_field(field_str) {
                fields.push(field_def);
            }
        }
    }
    
    fields
}

/// Parse a single field definition
fn parse_field(field_str: &str) -> Option<FieldDef> {
    let field_str = field_str.trim();
    
    // Check for array type (e.g., "tracks:track[]")
    if field_str.contains("[]") {
        if let Some(colon_pos) = field_str.find(':') {
            let name = field_str[..colon_pos].trim().to_string();
            let type_name = field_str[colon_pos+1..field_str.len()-2].trim().to_string();
            return Some(FieldDef {
                name,
                type_name: Some(type_name),
                kind: FieldKind::Array,
            });
        }
    }
    
    // Check for object type (e.g., "album:album")
    if let Some(colon_pos) = field_str.find(':') {
        let name = field_str[..colon_pos].trim().to_string();
        let type_name = field_str[colon_pos+1..].trim().to_string();
        return Some(FieldDef {
            name,
            type_name: Some(type_name),
            kind: FieldKind::Object,
        });
    }
    
    // Primitive type (just the field name)
    Some(FieldDef {
        name: field_str.to_string(),
        type_name: None,
        kind: FieldKind::Primitive,
    })
}







/// Parse data using type definitions
pub fn parse_data(input: &str, type_defs: &TypeDefs) -> Result<DataValue, String> {
    let input = input.trim();
    
    // Check if it's a typed value (e.g., "value: type" or "[...]: type")
    // Find the rightmost colon that's not inside braces/brackets
    if let Some(colon_pos) = find_main_colon(input) {
        let value_part = input[..colon_pos].trim();
        let type_name = input[colon_pos+1..].trim();
        
        // Check if it's a predefined type
        if let Some(field_defs) = type_defs.get(type_name) {
            return parse_typed_value(value_part, field_defs, type_defs);
        }
        
        // Check if it's an inline type definition (e.g., "{ title, duration }")
        if type_name.starts_with('{') && type_name.ends_with('}') {
            let fields_content = &type_name[1..type_name.len()-1];
            let inline_field_defs = parse_fields(fields_content);
            return parse_typed_value(value_part, &inline_field_defs, type_defs);
        }
    }
    
    // Check if it's an array
    if input.starts_with('[') && input.ends_with(']') {
        let content = &input[1..input.len()-1];
        let items = parse_array_items(content, type_defs)?;
        return Ok(DataValue::Array(items));
    }
    
    // Check if it's an object
    if input.starts_with('{') && input.ends_with('}') {
        let content = &input[1..input.len()-1];
        let items = parse_object_items(content, type_defs)?;
        return Ok(DataValue::Object(items));
    }
    
    // Single primitive value
    Ok(DataValue::Primitive(parse_primitive_value(input)))
}

/// Parse array items
fn parse_array_items(content: &str, type_defs: &TypeDefs) -> Result<Vec<DataValue>, String> {
    let mut items = Vec::new();
    let mut current_item = String::new();
    let mut brace_count = 0;
    let mut bracket_count = 0;
    
    for ch in content.chars() {
        match ch {
            '{' => {
                brace_count += 1;
                current_item.push(ch);
            }
            '}' => {
                brace_count -= 1;
                current_item.push(ch);
            }
            '[' => {
                bracket_count += 1;
                current_item.push(ch);
            }
            ']' => {
                bracket_count -= 1;
                current_item.push(ch);
            }
            ',' => {
                if brace_count == 0 && bracket_count == 0 {
                    let item = current_item.trim();
                    if !item.is_empty() {
                        items.push(parse_data(item, type_defs)?);
                    }
                    current_item.clear();
                } else {
                    current_item.push(ch);
                }
            }
            _ => current_item.push(ch),
        }
    }
    
    let item = current_item.trim();
    if !item.is_empty() {
        items.push(parse_data(item, type_defs)?);
    }
    
    Ok(items)
}

/// Parse object items (comma-separated values)
fn parse_object_items(content: &str, type_defs: &TypeDefs) -> Result<Vec<DataValue>, String> {
    let mut items = Vec::new();
    let mut current_item = String::new();
    let mut brace_count = 0;
    let mut bracket_count = 0;
    let mut in_string = false;
    let mut escape_next = false;
    
    for ch in content.chars() {
        if escape_next {
            current_item.push(ch);
            escape_next = false;
            continue;
        }
        
        match ch {
            '\\' if in_string => {
                escape_next = true;
                current_item.push(ch);
            }
            '"' => {
                in_string = !in_string;
                current_item.push(ch);
            }
            '{' if !in_string => {
                brace_count += 1;
                current_item.push(ch);
            }
            '}' if !in_string => {
                brace_count -= 1;
                current_item.push(ch);
            }
            '[' if !in_string => {
                bracket_count += 1;
                current_item.push(ch);
            }
            ']' if !in_string => {
                bracket_count -= 1;
                current_item.push(ch);
            }
            ',' if !in_string && brace_count == 0 && bracket_count == 0 => {
                let item = current_item.trim();
                if !item.is_empty() {
                    if let Some(colon_pos) = find_simple_colon(item) {
                        let key = item[..colon_pos].trim().to_string();
                        let value = item[colon_pos+1..].trim();
                        items.push(DataValue::Primitive(PrimitiveValue::String(key)));
                        items.push(parse_data(value, type_defs)?);
                    } else {
                        items.push(parse_data(item, type_defs)?);
                    }
                }
                current_item.clear();
            }
            _ => current_item.push(ch),
        }
    }
    
    let item = current_item.trim();
    if !item.is_empty() {
        if let Some(colon_pos) = find_simple_colon(item) {
            let key = item[..colon_pos].trim().to_string();
            let value = item[colon_pos+1..].trim();
            items.push(DataValue::Primitive(PrimitiveValue::String(key)));
            items.push(parse_data(value, type_defs)?);
        } else {
            items.push(parse_data(item, type_defs)?);
        }
    }
    
    Ok(items)
}

/// Parse a typed value using field definitions
fn parse_typed_value(value_part: &str, field_defs: &[FieldDef], type_defs: &TypeDefs) -> Result<DataValue, String> {
    let value_part = value_part.trim();
    
    // Check if it's an array
    if value_part.starts_with('[') && value_part.ends_with(']') {
        let content = &value_part[1..value_part.len()-1];
        let array_items = parse_array_items(content, type_defs)?;
        
        // Convert each array item to a typed object with field names
        let mut typed_items = Vec::new();
        for item in array_items {
            match item {
                DataValue::Object(items) => {
                    // Check if all items are key-value pairs (schema override case)
                    let all_key_value_pairs = check_if_all_key_value_pairs(&items);
                    
                    if all_key_value_pairs {
                        // All items are key-value pairs, ignore schema and use them directly
                        typed_items.push(DataValue::Object(items));
                    } else {
                        // Create a named object by mapping field names to values
                        let mut named_object = Vec::new();
                        let mut item_index = 0;
                        
                        // Process defined fields first
                        for field_def in field_defs.iter() {
                            if item_index < items.len() {
                                let typed_value = apply_field_type(&items[item_index], field_def, type_defs)?;
                                // Create key-value pair
                                named_object.push(DataValue::Primitive(PrimitiveValue::String(field_def.name.clone())));
                                named_object.push(typed_value);
                                item_index += 1;
                            }
                        }
                        
                        // Process any remaining key-value pairs
                        while item_index + 1 < items.len() {
                            if let DataValue::Primitive(PrimitiveValue::String(_)) = &items[item_index] {
                                // This looks like a key-value pair
                                named_object.push(items[item_index].clone());
                                named_object.push(items[item_index + 1].clone());
                                item_index += 2;
                            } else {
                                break;
                            }
                        }
                        
                        typed_items.push(DataValue::Object(named_object));
                    }
                }
                _ => {
                    return Err("Array items must be objects when using typed arrays".to_string());
                }
            }
        }
        return Ok(DataValue::Array(typed_items));
    }
    
    // Parse as single object - remove braces first
    let content = if value_part.starts_with('{') && value_part.ends_with('}') {
        &value_part[1..value_part.len()-1]
    } else {
        value_part
    };
    let items = parse_object_items(content, type_defs)?;
    
    // Check if all items are key-value pairs (schema override case)
    // A real key-value pair should come from "key: value" syntax in source
    let all_key_value_pairs = check_if_all_key_value_pairs(&items);
    
    if all_key_value_pairs {
        // All items are key-value pairs, ignore schema and use them directly
        return Ok(DataValue::Object(items));
    }
    
    // Create a named object by mapping field names to values
    let mut named_object = Vec::new();
    let mut item_index = 0;
    
    // Process defined fields first
    for field_def in field_defs.iter() {
        if item_index < items.len() {
            let typed_value = apply_field_type(&items[item_index], field_def, type_defs)?;
            // Create key-value pair
            named_object.push(DataValue::Primitive(PrimitiveValue::String(field_def.name.clone())));
            named_object.push(typed_value);
            item_index += 1;
        }
    }
    
    // Process any remaining key-value pairs
    while item_index + 1 < items.len() {
        if let DataValue::Primitive(PrimitiveValue::String(_)) = &items[item_index] {
            // This looks like a key-value pair
            named_object.push(items[item_index].clone());
            named_object.push(items[item_index + 1].clone());
            item_index += 2;
        } else {
            break;
        }
    }
    
    Ok(DataValue::Object(named_object))
}

/// Apply field type to a data value (handle nested objects and arrays)
fn apply_field_type(value: &DataValue, field_def: &FieldDef, type_defs: &TypeDefs) -> Result<DataValue, String> {
    match &field_def.kind {
        FieldKind::Primitive => Ok(value.clone()),
        FieldKind::Object => {
            if let Some(type_name) = &field_def.type_name {
                // Check if it's a predefined type
                if let Some(nested_field_defs) = type_defs.get(type_name) {
                    match value {
                        DataValue::Object(items) => {
                            // Apply the nested type to this object
                            let mut named_object = Vec::new();
                            let mut item_index = 0;
                            
                            // Process defined fields first
                            for nested_field_def in nested_field_defs.iter() {
                                if item_index < items.len() {
                                    let typed_value = apply_field_type(&items[item_index], nested_field_def, type_defs)?;
                                    // Create key-value pair
                                    named_object.push(DataValue::Primitive(PrimitiveValue::String(nested_field_def.name.clone())));
                                    named_object.push(typed_value);
                                    item_index += 1;
                                }
                            }
                            
                            // Process any remaining key-value pairs
                            while item_index + 1 < items.len() {
                                if let DataValue::Primitive(PrimitiveValue::String(_)) = &items[item_index] {
                                    named_object.push(items[item_index].clone());
                                    named_object.push(items[item_index + 1].clone());
                                    item_index += 2;
                                } else {
                                    break;
                                }
                            }
                            
                            Ok(DataValue::Object(named_object))
                        }
                        _ => Ok(value.clone())
                    }
                }
                // Check if it's an inline type definition (e.g., "{ age }")
                else if type_name.starts_with('{') && type_name.ends_with('}') {
                    let fields_content = &type_name[1..type_name.len()-1];
                    let inline_field_defs = parse_fields(fields_content);
                    match value {
                        DataValue::Object(items) => {
                            // Apply the inline type to this object
                            let mut named_object = Vec::new();
                            let mut item_index = 0;
                            
                            // Process defined fields first
                            for nested_field_def in inline_field_defs.iter() {
                                if item_index < items.len() {
                                    let typed_value = apply_field_type(&items[item_index], nested_field_def, type_defs)?;
                                    // Create key-value pair
                                    named_object.push(DataValue::Primitive(PrimitiveValue::String(nested_field_def.name.clone())));
                                    named_object.push(typed_value);
                                    item_index += 1;
                                }
                            }
                            
                            // Process any remaining key-value pairs
                            while item_index + 1 < items.len() {
                                if let DataValue::Primitive(PrimitiveValue::String(_)) = &items[item_index] {
                                    named_object.push(items[item_index].clone());
                                    named_object.push(items[item_index + 1].clone());
                                    item_index += 2;
                                } else {
                                    break;
                                }
                            }
                            
                            Ok(DataValue::Object(named_object))
                        }
                        _ => Ok(value.clone())
                    }
                } else {
                    Err(format!("Referenced type '{}' not found", type_name))
                }
            } else {
                Ok(value.clone())
            }
        }
        FieldKind::Array => {
            if let Some(element_type_name) = &field_def.type_name {
                if let Some(element_field_defs) = type_defs.get(element_type_name) {
                    match value {
                        DataValue::Array(items) => {
                            let mut typed_items = Vec::new();
                            for item in items {
                                match item {
                                    DataValue::Object(obj_items) => {
                                        // Apply the element type to each array item
                                        let mut named_object = Vec::new();
                                        let mut item_index = 0;
                                        
                                        // Process defined fields first
                                        for element_field_def in element_field_defs.iter() {
                                            if item_index < obj_items.len() {
                                                let typed_value = apply_field_type(&obj_items[item_index], element_field_def, type_defs)?;
                                                // Create key-value pair
                                                named_object.push(DataValue::Primitive(PrimitiveValue::String(element_field_def.name.clone())));
                                                named_object.push(typed_value);
                                                item_index += 1;
                                            }
                                        }
                                        
                                        // Process any remaining key-value pairs
                                        while item_index + 1 < obj_items.len() {
                                            if let DataValue::Primitive(PrimitiveValue::String(_)) = &obj_items[item_index] {
                                                named_object.push(obj_items[item_index].clone());
                                                named_object.push(obj_items[item_index + 1].clone());
                                                item_index += 2;
                                            } else {
                                                break;
                                            }
                                        }
                                        
                                        typed_items.push(DataValue::Object(named_object));
                                    }
                                    _ => typed_items.push(item.clone())
                                }
                            }
                            Ok(DataValue::Array(typed_items))
                        }
                        _ => Ok(value.clone())
                    }
                } else {
                    Err(format!("Referenced array element type '{}' not found", element_type_name))
                }
            } else {
                Ok(value.clone())
            }
        }
    }
}


