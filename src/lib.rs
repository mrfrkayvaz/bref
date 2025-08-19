use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::{PyDict, PyList};

mod parser;
use parser::{parse_type_definitions, parse_data, DataValue, PrimitiveValue, TypeDefs};

#[cfg(test)]
mod tests;

#[pyfunction]
fn parse(s: &str, py: Python<'_>) -> PyResult<PyObject> {
    // Tip tanımlamalarını çıkar
    let type_defs = parse_type_definitions(s);

    // Veri satırlarını filtrele
    let data_lines: Vec<_> = s
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty() && !line.starts_with(':'))
        .collect();

    // Eğer veri yoksa sadece type_defs dön
    if data_lines.is_empty() {
        let result = PyDict::new_bound(py);
        result.set_item("type_defs", convert_type_defs_to_python(type_defs, py)?)?;
        result.set_item("data", py.None())?;
        return Ok(result.into());
    }

    // Veriyi parse et
    let data_result = parse_data(&data_lines.join("\n"), &type_defs);

    match data_result {
        Ok(data_value) => {
            let result = PyDict::new_bound(py);
            result.set_item("type_defs", convert_type_defs_to_python(type_defs, py)?)?;
            result.set_item("data", convert_data_value_to_python(data_value, py)?)?;
            Ok(result.into())
        }
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(e)),
    }
}

/// Rust type_defs → Python dict
fn convert_type_defs_to_python(type_defs: TypeDefs, py: Python<'_>) -> PyResult<PyObject> {
    let py_dict = PyDict::new_bound(py);

    for (type_name, fields) in type_defs {
        let py_fields = PyList::empty_bound(py);
        for field in fields {
            let py_field = PyDict::new_bound(py);
            py_field.set_item("name", &field.name)?;
            py_field.set_item("type_name", &field.type_name)?;
            py_field.set_item(
                "kind",
                match field.kind {
                    parser::FieldKind::Primitive => "Primitive",
                    parser::FieldKind::Object => "Object",
                    parser::FieldKind::Array => "Array",
                },
            )?;
            py_fields.append(py_field)?;
        }
        py_dict.set_item(type_name, py_fields)?;
    }

    Ok(py_dict.into())
}

/// Rust DataValue → Python objesi
fn convert_data_value_to_python(data_value: DataValue, py: Python<'_>) -> PyResult<PyObject> {
    Ok(match data_value {
        DataValue::Primitive(primitive) => convert_primitive_to_python(primitive, py)?,

        DataValue::Object(items) => {
            // structured key-value dict mi kontrol et
            if items.len() % 2 == 0
                && !items.is_empty()
                && items.chunks(2).all(|pair| {
                    matches!(pair[0], DataValue::Primitive(PrimitiveValue::String(_)))
                })
            {
                let py_dict = PyDict::new_bound(py);
                for pair in items.chunks(2) {
                    if let DataValue::Primitive(PrimitiveValue::String(key)) = &pair[0] {
                        let value = convert_data_value_to_python(pair[1].clone(), py)?;
                        py_dict.set_item(key, value)?;
                    }
                }
                py_dict.into()
            } else {
                let py_list = PyList::empty_bound(py);
                for item in items {
                    py_list.append(convert_data_value_to_python(item, py)?)?;
                }
                py_list.into()
            }
        }

        DataValue::Array(items) => {
            let py_list = PyList::empty_bound(py);
            for item in items {
                py_list.append(convert_data_value_to_python(item, py)?)?;
            }
            py_list.into()
        }
    })
}

/// Rust PrimitiveValue → Python objesi
fn convert_primitive_to_python(primitive: PrimitiveValue, py: Python<'_>) -> PyResult<PyObject> {
    Ok(match primitive {
        PrimitiveValue::String(s) => s.into_py(py),
        PrimitiveValue::Integer(i) => i.into_py(py),
        PrimitiveValue::Float(f) => f.into_py(py),
        PrimitiveValue::Boolean(b) => b.into_py(py),
        PrimitiveValue::Null => py.None().into(),
    })
}

#[pyfunction]
fn to_json(s: &str, py: Python<'_>) -> PyResult<String> {
    // sadece veriyi parse et
    let type_defs = parse_type_definitions(s);

    let data_lines: Vec<_> = s
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty() && !line.starts_with(':'))
        .collect();

    if data_lines.is_empty() {
        return Ok("null".to_string());
    }

    let data_result = parse_data(&data_lines.join("\n"), &type_defs)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))?;
    let py_data = convert_data_value_to_python(data_result, py)?;

    // JSON’a çevir
    let json_module = py.import_bound("json")?;
    let json_dumps = json_module.getattr("dumps")?;
    let kwargs = PyDict::new_bound(py);
    kwargs.set_item("ensure_ascii", false)?;
    let json_string = json_dumps.call((py_data,), Some(&kwargs))?;
    let json_str: String = json_string.extract()?;

    Ok(json_str)
}

#[pymodule]
fn brefpy(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(to_json, m)?)?;
    Ok(())
}
