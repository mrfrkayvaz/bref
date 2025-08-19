use crate::parser::*;

#[test]
fn test_type_definitions_parsing() {
    let input = r#"
    :song { title, duration, genre, album:album, streams, is_favorite }
    :album { title, year, band:band, tracks:track[] }
    :track { title }
    :band { name, country }
    "#;

    let type_defs = parse_type_definitions(input);
    
    // Test that all types are parsed
    assert_eq!(type_defs.len(), 4);
    assert!(type_defs.contains_key("song"));
    assert!(type_defs.contains_key("album"));
    assert!(type_defs.contains_key("track"));
    assert!(type_defs.contains_key("band"));
    
    // Test song type fields
    let song_fields = &type_defs["song"];
    assert_eq!(song_fields.len(), 6);
    assert_eq!(song_fields[0].name, "title");
    assert_eq!(song_fields[0].type_name, None);
    assert!(matches!(song_fields[0].kind, FieldKind::Primitive));
    
    assert_eq!(song_fields[3].name, "album");
    assert_eq!(song_fields[3].type_name, Some("album".to_string()));
    assert!(matches!(song_fields[3].kind, FieldKind::Object));
    
    // Test album type fields
    let album_fields = &type_defs["album"];
    assert_eq!(album_fields.len(), 4);
    assert_eq!(album_fields[3].name, "tracks");
    assert_eq!(album_fields[3].type_name, Some("track".to_string()));
    assert!(matches!(album_fields[3].kind, FieldKind::Array));
}

#[test]
fn test_primitive_value_parsing() {
    // Test string
    let result = parse_primitive_value("\"Hello World\"");
    assert!(matches!(result, PrimitiveValue::String(s) if s == "Hello World"));
    
    // Test integer
    let result = parse_primitive_value("42");
    assert!(matches!(result, PrimitiveValue::Integer(42)));
    
    // Test float
    let result = parse_primitive_value("3.14");
    assert!(matches!(result, PrimitiveValue::Float(f) if (f - 3.14).abs() < 0.001));
    
    // Test boolean
    let result = parse_primitive_value("true");
    assert!(matches!(result, PrimitiveValue::Boolean(true)));
    
    let result = parse_primitive_value("false");
    assert!(matches!(result, PrimitiveValue::Boolean(false)));
    
    // Test null
    let result = parse_primitive_value("null");
    assert!(matches!(result, PrimitiveValue::Null));
}

#[test]
fn test_simple_array_parsing() {
    let type_defs = parse_type_definitions(":track { title }");
    
    let input = r#"[
        { "Track 1" },
        { "Track 2" }
    ]: track"#;
    
    let result = parse_data(input, &type_defs);
    
    match result {
        Ok(DataValue::Array(items)) => {
            assert_eq!(items.len(), 2);
            // Add more specific assertions based on expected structure
        }
        _ => panic!("Expected array result"),
    }
}

#[test]
fn test_complex_data_parsing() {
    let input = r#"
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band, tracks:track[] }
:track { title }
:band { name, country }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" }, [{"Love of My Life"}] },
    1980000000, true
  }
]: song
"#;

    let type_defs = parse_type_definitions(input);
    
    // Find the data part (lines that don't start with ':')
    let mut data_lines = Vec::new();
    for line in input.lines() {
        let line = line.trim();
        if !line.is_empty() && !line.starts_with(':') {
            data_lines.push(line);
        }
    }
    
    let data_str = data_lines.join("\n");
    let result = parse_data(&data_str, &type_defs);
    
    match result {
        Ok(DataValue::Array(items)) => {
            assert_eq!(items.len(), 1);
            println!("Successfully parsed complex data with {} items", items.len());
        }
        Err(e) => {
            panic!("Failed to parse complex data: {}", e);
        }
        _ => panic!("Expected array result"),
    }
}

#[test]
fn test_empty_type_definitions() {
    let input = "";
    let type_defs = parse_type_definitions(input);
    assert_eq!(type_defs.len(), 0);
}

#[test]
fn test_single_type_definition() {
    let input = ":simple { name, value }";
    let type_defs = parse_type_definitions(input);
    
    assert_eq!(type_defs.len(), 1);
    assert!(type_defs.contains_key("simple"));
    
    let fields = &type_defs["simple"];
    assert_eq!(fields.len(), 2);
    assert_eq!(fields[0].name, "name");
    assert_eq!(fields[1].name, "value");
}
