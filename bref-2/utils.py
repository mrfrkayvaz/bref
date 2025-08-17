import re
from typing import Dict, List, Tuple, Union, Any
from enum import Enum

class FieldType(Enum):
    TYPE_REFERENCE = "type_reference"
    DEFAULT_VALUE = "default_value"

SchemaField = Union[str, Tuple[str, str, FieldType]]
Schema = List[SchemaField]

def parse_schema_fields(text: str) -> Schema:
    """
    '{ title, year, artist:artist, test: { age }, is_favorite: false }' içindeki alanları schema listesine çevirir.
    Dönüş: ["title", "year", ("artist", "artist"), ("test", ["age"]), ("is_favorite", "false")]
    """
    inner = text.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]

    parts = [p.strip() for p in inner.split(",") if p.strip()]
    fields: Schema = []
    for p in parts:
        if ":" in p:
            key, tname = p.split(":", 1)
            key = key.strip()
            tname = tname.strip()
            
            # Nested inline schema kontrolü: test: { age }
            if tname.startswith("{") and tname.endswith("}"):
                # Nested schema'yı parse et
                nested_schema = parse_schema_fields(tname)
                fields.append((key, nested_schema))
            else:
                # Default value kontrolü: is_favorite: false
                if tname.lower() in ('true', 'false', 'null'):
                    # Boolean veya null default value
                    default_val = None if tname.lower() == 'null' else tname.lower() == 'true'
                    fields.append((key, default_val, FieldType.DEFAULT_VALUE))
                elif tname.replace('.', '').replace('-', '').isdigit():
                    # Numeric default value
                    default_val = float(tname) if '.' in tname else int(tname)
                    fields.append((key, default_val, FieldType.DEFAULT_VALUE))
                elif tname.startswith('"') and tname.endswith('"'):
                    # String default value
                    default_val = tname[1:-1]
                    fields.append((key, default_val, FieldType.DEFAULT_VALUE))
                else:
                    # Type reference: artist:artist veya album:album
                    # Eğer tname bir identifier ise (sadece harf/rakam/underscore içeriyorsa) type reference
                    if tname.replace('_', '').isalnum():
                        fields.append((key, tname, FieldType.TYPE_REFERENCE))  # Type reference
                    else:
                        # Diğer durumlar için string olarak kabul et
                        fields.append((key, tname, FieldType.DEFAULT_VALUE))
        else:
            fields.append(p)
    return fields


def parse_value_definition(text: str) -> List[Any]:
    """
    ':ist { "Türkiye", "Istanbul", "Maltepe" }' gibi value definition'ları parse eder.
    Dönüş: ["Türkiye", "Istanbul", "Maltepe"]
    """
    inner = text.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]

    parts = [p.strip() for p in inner.split(",") if p.strip()]
    values = []
    for p in parts:
        # String değerleri parse et
        if p.startswith('"') and p.endswith('"'):
            values.append(p[1:-1])  # Tırnakları kaldır
        # Sayısal değerleri parse et
        elif p.replace('.', '').replace('-', '').isdigit():
            if '.' in p:
                values.append(float(p))
            else:
                values.append(int(p))
        # Boolean değerleri parse et
        elif p.lower() in ('true', 'false'):
            values.append(p.lower() == 'true')
        # null değerini parse et
        elif p.lower() == 'null':
            values.append(None)
        else:
            # Diğer durumlarda string olarak kabul et
            values.append(p)
    return values


def parse_type_definitions(content: str) -> Tuple[Dict[str, Schema], Dict[str, List[Any]], str]:
    """
    Başındaki/arasındaki tip tanımı ve value definition satırlarını yakalar ve kalan veri gövdesini döndürür.
    ':artist { name, country }' gibi type definitions ve ':ist { "Türkiye", "Istanbul", "Maltepe" }' gibi value definitions bekler.
    """
    type_defs: Dict[str, Schema] = {}
    value_defs: Dict[str, List[Any]] = {}
    remaining_lines: List[str] = []

    # Type definition pattern: :name { field1, field2:type, ... }
    type_pattern = re.compile(r'^\s*:(?P<name>[A-Za-z_]\w*)\s*(?P<body>\{[^}]*\})\s*$')
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        m = type_pattern.match(line)
        if m:
            name = m.group("name")
            body = m.group("body")
            
            # Value definition mu yoksa type definition mu kontrol et
            # Type definition'da field:type formatı olur, value definition'da sadece değerler olur
            parts = [p.strip() for p in body.split(",") if p.strip()]
            has_field_type_format = any(':' in part and not part.startswith('"') for part in parts)
            has_quoted_values = any(part.startswith('"') for part in parts)
            
            if has_field_type_format:
                type_defs[name] = parse_schema_fields(body)
            elif has_quoted_values:
                value_defs[name] = parse_value_definition(body)
            else:
                type_defs[name] = parse_schema_fields(body)
        else:
            remaining_lines.append(line)

    return type_defs, value_defs, "\n".join(remaining_lines).strip()
