use crate::types::{DataValue, PrimitiveValue};

pub fn find_simple_colon(input: &str) -> Option<usize> {
    let mut in_string = false;
    let mut escape_next = false;
    
    for (i, ch) in input.char_indices() {
        if escape_next {
            escape_next = false;
            continue;
        }
        
        match ch {
            '\\' if in_string => escape_next = true,
            '"' => in_string = !in_string,
            ':' if !in_string => {
                let key_part = input[..i].trim();
                if key_part.chars().all(|c| c.is_alphanumeric() || c == '_') {
                    return Some(i);
                }
            }
            _ => {}
        }
    }
    
    None
}

pub fn check_if_all_key_value_pairs(items: &[DataValue]) -> bool {
    if items.len() % 2 != 0 || items.is_empty() {
        return false;
    }
    
    for pair in items.chunks(2) {
        if let DataValue::Primitive(PrimitiveValue::String(key)) = &pair[0] {
            if !key.chars().all(|c| c.is_alphanumeric() || c == '_') {
                return false;
            }
            if key.len() > 20 {
                return false;
            }
        } else {
            return false;
        }
    }
    
    true
}

pub fn find_main_colon(input: &str) -> Option<usize> {
    let mut brace_count = 0;
    let mut bracket_count = 0;
    let mut in_string = false;
    let mut escape_next = false;
    let mut last_colon = None;
    
    for (i, ch) in input.char_indices() {
        if escape_next {
            escape_next = false;
            continue;
        }
        
        match ch {
            '\\' if in_string => escape_next = true,
            '"' => in_string = !in_string,
            '{' if !in_string => brace_count += 1,
            '}' if !in_string => brace_count -= 1,
            '[' if !in_string => bracket_count += 1,
            ']' if !in_string => bracket_count -= 1,
            ':' if !in_string && brace_count == 0 && bracket_count == 0 => {
                last_colon = Some(i);
            }
            _ => {}
        }
    }
    
    last_colon
}

pub fn parse_primitive_value(input: &str) -> PrimitiveValue {
    let input = input.trim();
    
    if input == "true" {
        return PrimitiveValue::Boolean(true);
    }
    if input == "false" {
        return PrimitiveValue::Boolean(false);
    }
    
    if input == "null" {
        return PrimitiveValue::Null;
    }
    
    if let Ok(int_val) = input.parse::<i64>() {
        return PrimitiveValue::Integer(int_val);
    }
    if let Ok(float_val) = input.parse::<f64>() {
        return PrimitiveValue::Float(float_val);
    }
    
    let value = if input.starts_with('"') && input.ends_with('"') {
        input[1..input.len()-1].to_string()
    } else {
        input.to_string()
    };
    
    PrimitiveValue::String(value)
}
