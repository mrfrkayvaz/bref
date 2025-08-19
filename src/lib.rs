use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn parse(s: &str) -> PyResult<String> {
    Ok(s.to_string())  // sadece return ediyor
}

#[pymodule]
fn bref(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
