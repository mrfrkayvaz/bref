use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::{PyDict, PyList};

mod parser;
use parser::{parse_type_definitions, parse_data, DataValue, PrimitiveValue, TypeDefs};

#[cfg(test)]
mod tests;

#[pyfunction]
fn parse(s: &str, py: Python<'_>) -> PyResult<PyObject> {
    // First, extract type definitions
    let type_defs = parse_type_definitions(s);
    
    // Find the data part (lines that don't start with ':')
    let mut data_lines = Vec::new();
    for line in s.lines() {
        let line = line.trim();
        if !line.is_empty() && !line.starts_with(':') {
            data_lines.push(line);
        }
    }
    
    // If no data lines found, return only type definitions
    if data_lines.is_empty() {
        let result = PyDict::new_bound(py);
        result.set_item("type_defs", convert_type_defs_to_python(type_defs, py))?;
        result.set_item("data", py.None())?;
        return Ok(result.into());
    }
    
    // Parse the data using type definitions
    let data_result = parse_data(&data_lines.join("\n"), &type_defs);
    
    match data_result {
        Ok(data_value) => {
            // Convert both type definitions and data to Python
            let result = PyDict::new_bound(py);
            result.set_item("type_defs", convert_type_defs_to_python(type_defs, py))?;
            result.set_item("data", convert_data_value_to_python(data_value, py))?;
            Ok(result.into())
        }
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(e)),
    }
}

/// Convert Rust type definitions to Python dict
fn convert_type_defs_to_python(type_defs: TypeDefs, py: Python<'_>) -> PyObject {
    let py_dict = PyDict::new_bound(py);
    
    for (type_name, fields) in type_defs {
        let py_fields = PyList::empty_bound(py);
        for field in fields {
            let py_field = PyDict::new_bound(py);
            py_field.set_item("name", field.name).unwrap();
            py_field.set_item("type_name", field.type_name).unwrap();
            py_field.set_item("kind", match field.kind {
                parser::FieldKind::Primitive => "Primitive",
                parser::FieldKind::Object => "Object",
                parser::FieldKind::Array => "Array",
            }).unwrap();
            py_fields.append(py_field).unwrap();
        }
        py_dict.set_item(type_name, py_fields).unwrap();
    }
    
    py_dict.into()
}

/// Convert Rust DataValue to Python object
fn convert_data_value_to_python(data_value: DataValue, py: Python<'_>) -> PyObject {
    match data_value {
        DataValue::Primitive(primitive) => convert_primitive_to_python(primitive, py),
        DataValue::Object(items) => {
            // Check if this is a key-value paired object (structured object)
            if items.len() % 2 == 0 && items.len() > 0 {
                // Check if this follows key-value pattern
                let mut is_structured = true;
                for i in (0..items.len()).step_by(2) {
                    if let DataValue::Primitive(PrimitiveValue::String(_)) = &items[i] {
                        // This looks like a key
                        continue;
                    } else {
                        is_structured = false;
                        break;
                    }
                }
                
                if is_structured {
                    // Convert to Python dict
                    let py_dict = PyDict::new_bound(py);
                    for i in (0..items.len()).step_by(2) {
                        if let DataValue::Primitive(PrimitiveValue::String(key)) = &items[i] {
                            let value = convert_data_value_to_python(items[i + 1].clone(), py);
                            py_dict.set_item(key, value).unwrap();
                        }
                    }
                    return py_dict.into();
                }
            }
            
            // Fall back to list for non-structured objects
            let py_list = PyList::empty_bound(py);
            for item in items {
                py_list.append(convert_data_value_to_python(item, py)).unwrap();
            }
            py_list.into()
        }
        DataValue::Array(items) => {
            let py_list = PyList::empty_bound(py);
            for item in items {
                py_list.append(convert_data_value_to_python(item, py)).unwrap();
            }
            py_list.into()
        }
    }
}

/// Convert Rust PrimitiveValue to Python object
fn convert_primitive_to_python(primitive: PrimitiveValue, py: Python<'_>) -> PyObject {
    match primitive {
        PrimitiveValue::String(s) => s.into_py(py),
        PrimitiveValue::Integer(i) => i.into_py(py),
        PrimitiveValue::Float(f) => f.into_py(py),
        PrimitiveValue::Boolean(b) => b.into_py(py),
        PrimitiveValue::Null => py.None().into(),
    }
}

#[pyfunction]
fn toJSON(s: &str, py: Python<'_>) -> PyResult<String> {
    // Parse the bref string using our existing parse function
    let parsed_result = parse(s, py)?;
    
    // Extract only the 'data' part from the parsed result
    let dict = parsed_result.downcast_bound::<PyDict>(py)?;
    let data_value = match dict.get_item("data")? {
        Some(data) => data.into(),
        None => py.None(),
    };
    
    // Convert the data part to JSON string
    let json_module = py.import_bound("json")?;
    let json_dumps = json_module.getattr("dumps")?;
    
    // Call json.dumps with ensure_ascii=False for better Unicode support
    let kwargs = pyo3::types::PyDict::new_bound(py);
    kwargs.set_item("ensure_ascii", false)?;
    
    let json_string = json_dumps.call((data_value,), Some(&kwargs))?;
    let json_str: String = json_string.extract()?;
    
    Ok(json_str)
}

#[pymodule]
fn bref(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(toJSON, m)?)?;
    Ok(())
}
