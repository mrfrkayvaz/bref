use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use crate::types::{DataValue, PrimitiveValue, TypeDefs, FieldDef, FieldKind};

pub fn convert_type_defs_to_python(type_defs: TypeDefs, py: Python<'_>) -> PyResult<PyObject> {
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
                    FieldKind::Primitive => "Primitive",
                    FieldKind::Object => "Object",
                    FieldKind::Array => "Array",
                },
            )?;
            py_fields.append(py_field)?;
        }
        py_dict.set_item(type_name, py_fields)?;
    }

    Ok(py_dict.into())
}

pub fn convert_data_value_to_python(data_value: DataValue, py: Python<'_>) -> PyResult<PyObject> {
    Ok(match data_value {
        DataValue::Primitive(primitive) => convert_primitive_to_python(primitive, py)?,

        DataValue::Object(items) => {
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

pub fn convert_primitive_to_python(primitive: PrimitiveValue, py: Python<'_>) -> PyResult<PyObject> {
    Ok(match primitive {
        PrimitiveValue::String(s) => s.into_py(py),
        PrimitiveValue::Integer(i) => i.into_py(py),
        PrimitiveValue::Float(f) => f.into_py(py),
        PrimitiveValue::Boolean(b) => b.into_py(py),
        PrimitiveValue::Null => py.None().into(),
    })
}
