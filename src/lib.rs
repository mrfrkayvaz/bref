use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::PyDict;

mod types;
mod conversion;
mod utils;
mod parser;

use types::{DataValue, PrimitiveValue, TypeDefs};
use conversion::{convert_type_defs_to_python, convert_data_value_to_python};
use parser::{parse_type_definitions, parse_data};

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
