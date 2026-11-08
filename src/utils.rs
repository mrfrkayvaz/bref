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

    for i in (0..items.len()).step_by(2) {
        if let DataValue::Primitive(PrimitiveValue::String(ref key)) = items[i] {
            if key.len() > 20 {
                return false;
            }
            if !key.as_bytes().iter().all(|&c| c.is_ascii_alphanumeric() || c == b'_') {
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

    for (i, b) in input.bytes().enumerate() {
        if escape_next {
            escape_next = false;
            continue;
        }

        match b {
            b'\\' if in_string => escape_next = true,
            b'"' => in_string = !in_string,
            b'{' if !in_string => brace_count += 1,
            b'}' if !in_string => brace_count -= 1,
            b'[' if !in_string => bracket_count += 1,
            b']' if !in_string => bracket_count -= 1,
            b':' if !in_string && brace_count == 0 && bracket_count == 0 => {
                last_colon = Some(i);
            }
            _ => {}
        }
    }
    last_colon
}

pub fn parse_primitive_value(input: &str) -> PrimitiveValue {
    let input = input.trim();

    match input {
        "true"  => return PrimitiveValue::Boolean(true),
        "false" => return PrimitiveValue::Boolean(false),
        "null"  => return PrimitiveValue::Null,
        _ => {}
    }

    // sayı kontrolü (hız için önce byte check)
    if let Some(first) = input.as_bytes().first() {
        if first.is_ascii_digit() || *first == b'-' {
            if input.contains('.') {
                if let Ok(f) = input.parse::<f64>() {
                    return PrimitiveValue::Float(f);
                }
            } else {
                if let Ok(i) = input.parse::<i64>() {
                    return PrimitiveValue::Integer(i);
                }
            }
        }
    }

    // string
    if let Some(stripped) = input.strip_prefix('"').and_then(|s| s.strip_suffix('"')) {
        return PrimitiveValue::String(stripped.to_string());
    }

    PrimitiveValue::String(input.to_string())
}

