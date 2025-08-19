use std::collections::HashMap;
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub enum FieldKind {
    Primitive,
    Object,
    Array,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FieldDef {
    pub name: String,
    pub type_name: Option<String>,
    pub kind: FieldKind,
}

pub type TypeDefs = HashMap<String, Vec<FieldDef>>;

#[derive(Debug, Clone, Serialize)]
pub enum DataValue {
    Primitive(PrimitiveValue),
    Object(Vec<DataValue>),
    Array(Vec<DataValue>),
}

#[derive(Debug, Clone, Serialize)]
pub enum PrimitiveValue {
    String(String),
    Integer(i64),
    Float(f64),
    Boolean(bool),
    Null,
}
