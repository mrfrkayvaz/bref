from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union, Dict

from .utils import parse_type_definitions, parse_schema_fields, Schema, SchemaField

# --- Basit AST düğümleri ---

@dataclass
class Node:
    """AST düğümü: primitive | list(tuple-vari) | array"""
    kind: str  # "primitive" | "list" | "array"
    value: Any  # primitive için python değeri; list/array için List[Node]
    type_ann: Optional[Union[str, Schema]] = None  # "song" veya inline şema listesi


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, text: str):
        self.s = text
        self.i = 0
        self.n = len(text)

    # ---- low-level yardımcılar ----
    def eof(self) -> bool:
        return self.i >= self.n

    def peek(self) -> str:
        return self.s[self.i] if not self.eof() else ""

    def get(self) -> str:
        ch = self.peek()
        self.i += 1
        return ch

    def skip_ws(self):
        while not self.eof() and self.peek().isspace():
            self.i += 1

    # ---- parse giriş noktası ----
    def parse_value(self) -> Node:
        self.skip_ws()
        if self.eof():
            raise ParseError("Beklenmeyen dosya sonu")

        ch = self.peek()

        if ch == '{':
            return self.parse_list_node()
        if ch == '[':
            return self.parse_array_node()
        if ch == '"':
            return Node("primitive", self.parse_string())
        # literal (true/false/null) veya sayı
        if ch == '-' or ch.isdigit():
            return Node("primitive", self.parse_number())
        # true/false/null
        ident = self.try_parse_identifier_literal()
        if ident == "null":
            return Node("primitive", None)
        if ident is not None:
            return Node("primitive", ident)
        # default value (.)
        if ch == '.':
            self.get()  # . karakterini tüket
            return Node("primitive", "DEFAULT")
        
        # value definition reference (identifier)
        if ch.isalpha() or ch == '_':
            return Node("primitive", self.read_identifier())

        raise ParseError(f"Beklenmeyen karakter: {ch} @ {self.i}")

    def parse_list_node(self) -> Node:
        # { v1, v2, ... } veya { v1, v2, key: value, ... }
        assert self.get() == '{'
        items: List[Node] = []
        self.skip_ws()
        if self.peek() == '}':
            self.get()
            type_ann = self.parse_type_annotation()
            return Node("list", items, type_ann)

        while True:
            # Key-value pair kontrolü
            if self.peek().isalpha() or self.peek() == '_':
                # Identifier başlangıcı - key-value pair olabilir
                start_pos = self.i
                key = self.read_identifier()
                self.skip_ws()
                
                if self.peek() == ':':
                    # Key-value pair: key: value
                    self.get()  # : karakterini tüket
                    self.skip_ws()
                    value = self.parse_value()
                    items.append(Node("key_value", (key, value)))
                else:
                    # Sadece identifier - pozisyonu geri al ve normal value olarak parse et
                    self.i = start_pos
                    items.append(self.parse_value())
            else:
                # Normal value
                items.append(self.parse_value())
            
            self.skip_ws()
            ch = self.peek()
            if ch == ',':
                self.get()
                self.skip_ws()
                continue
            if ch == '}':
                self.get()
                break
            raise ParseError(f"List içinde beklenmeyen karakter: {ch} @ {self.i}")

        type_ann = self.parse_type_annotation()
        return Node("list", items, type_ann)

    def parse_array_node(self) -> Node:
        # [ v1, v2, ... ]
        assert self.get() == '['
        items: List[Node] = []
        self.skip_ws()
        if self.peek() == ']':
            self.get()
            type_ann = self.parse_type_annotation()
            return Node("array", items, type_ann)

        while True:
            items.append(self.parse_value())
            self.skip_ws()
            ch = self.peek()
            if ch == ',':
                self.get()
                self.skip_ws()
                continue
            if ch == ']':
                self.get()
                break
            raise ParseError(f"Array içinde beklenmeyen karakter: {ch} @ {self.i}")

        type_ann = self.parse_type_annotation()
        return Node("array", items, type_ann)

    def parse_type_annotation(self) -> Optional[Union[str, Schema]]:
        # opsiyonel:  : typeName  |  : { fields }
        self.skip_ws()
        if self.eof() or self.peek() != ':':
            return None
        self.get()
        self.skip_ws()
        ch = self.peek()
        if ch == '{':
            schema_text = self.read_braced()
            return parse_schema_fields(schema_text)
        # else identifier
        name = self.read_identifier()
        return name

    # ---- basit token parsers ----
    def parse_string(self) -> str:
        # JSON string gibi: escape destekli
        assert self.get() == '"'
        buf = ['"']
        while not self.eof():
            c = self.get()
            buf.append(c)
            if c == '\\':  # escape
                if not self.eof():
                    buf.append(self.get())
                continue
            if c == '"':
                break
        import json as _json
        return _json.loads(''.join(buf))

    def parse_number(self) -> Union[int, float]:
        start = self.i
        ch = self.peek()
        if ch == '-':
            self.get()
        while not self.eof() and self.peek().isdigit():
            self.get()
        if not self.eof() and self.peek() == '.':
            self.get()
            while not self.eof() and self.peek().isdigit():
                self.get()
        num_str = self.s[start:self.i]
        if '.' in num_str:
            return float(num_str)
        return int(num_str)

    def try_parse_identifier_literal(self) -> Optional[Union[bool, None]]:
        # true / false / null
        for lit, val in (("true", True), ("false", False), ("null", "null")):
            if self.s.startswith(lit, self.i):
                self.i += len(lit)
                return val
        return None

    def read_identifier(self) -> str:
        self.skip_ws()
        start = self.i
        if self.eof():
            raise ParseError("Tip adı bekleniyordu")
        ch = self.peek()
        if not (ch.isalpha() or ch == '_'):
            raise ParseError(f"Geçersiz tip adı başlangıcı: {ch}")
        self.get()
        while not self.eof() and (self.peek().isalnum() or self.peek() == '_'):
            self.get()
        return self.s[start:self.i]

    def read_braced(self) -> str:
        # '{' ile başlıyorsa, dengeli kapanana kadar oku ve string olarak döndür
        self.skip_ws()
        if self.peek() != '{':
            raise ParseError("'{ ... }' şeması bekleniyordu")
        start = self.i
        depth = 0
        while not self.eof():
            c = self.get()
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return self.s[start:self.i]
            elif c == '"':
                # string içindeki braketleri atlamak için tırnak içini geç
                self._skip_string_inside('"')
        raise ParseError("Kapanmayan '{'")

    def _skip_string_inside(self, quote: str):
        # parse_string'i çağırmadan tırnaklı içeriği atlamak için
        while not self.eof():
            c = self.get()
            if c == '\\':
                if not self.eof():
                    self.get()
                continue
            if c == quote:
                break


# ---- Şema uygulama (AST -> JSON) ----

class Materializer:
    def __init__(self, type_defs: Dict[str, Schema], value_defs: Dict[str, List[Any]]):
        self.type_defs = type_defs
        self.value_defs = value_defs

    def build(self, node: Node, expected_type: Optional[Union[str, Schema]] = None) -> Any:
        # Etkili tip: düğümün kendi tipi > beklenen tip
        effective_type = node.type_ann if node.type_ann is not None else expected_type

        if node.kind == "primitive":
            # Value definition reference kontrolü
            if isinstance(node.value, str) and node.value in self.value_defs:
                value_list = self.value_defs[node.value]
                # Eğer beklenen bir tip varsa, value list'ini o schema'ya göre object'e dönüştür
                if expected_type is not None:
                    schema = self._resolve_schema(expected_type)
                    return self._map_value_list_to_object(value_list, schema)
                return value_list
            return node.value

        if node.kind == "array":
            # Eğer bir tipe sahipse -> her elemana uygula
            if effective_type is not None:
                return [self.build(child, effective_type) for child in node.value]
            # Aksi halde ham liste
            return [self.build(child, None) for child in node.value]

        if node.kind == "list":
            # Tip yoksa ham liste döndür (örneklerinde hep tipli geliyor)
            if effective_type is None:
                return [self.build(child, None) for child in node.value]
            schema = self._resolve_schema(effective_type)
            return self._map_list_to_object(node.value, schema)

        raise ParseError("Bilinmeyen düğüm türü")

    def _resolve_schema(self, t: Union[str, Schema]) -> Schema:
        if isinstance(t, list):
            return t  # inline şema
        # named type
        if t not in self.type_defs:
            raise ParseError(f"Tanımsız tip: {t}")
        return self.type_defs[t]

    def _map_list_to_object(self, items: List[Node], schema: Schema) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        schema_idx = 0
        
        for item in items:
            if item.kind == "key_value":
                # Key-value pair: (key, value)
                key, value_node = item.value
                result[key] = self.build(value_node, None)
            else:
                # Normal value - schema'ya göre map et
                if schema_idx < len(schema):
                    field = schema[schema_idx]
                    # DEFAULT node kontrolü
                    if (isinstance(item, Node) and 
                        item.kind == "primitive" and 
                        item.value == "DEFAULT"):
                        # Default value kullan
                        if isinstance(field, tuple):
                            key, sub_t = field
                            if isinstance(sub_t, (bool, int, float, str, type(None))):
                                result[key] = sub_t
                            else:
                                result[key] = None
                        else:
                            result[field] = None
                    else:
                        # Normal value
                        if isinstance(field, tuple):
                            key, sub_t = field
                            result[key] = self.build(item, sub_t)
                        else:
                            result[field] = self.build(item, None)
                    schema_idx += 1
                else:
                    # Schema'dan fazla item var - key-value pair olarak ekle
                    if item.kind == "key_value":
                        key, value_node = item.value
                        result[key] = self.build(value_node, None)
        
        # Eksik schema field'ları için default value kullan
        while schema_idx < len(schema):
            field = schema[schema_idx]
            if isinstance(field, tuple):
                key, sub_t = field
                if isinstance(sub_t, (bool, int, float, str, type(None))):
                    result[key] = sub_t
                else:
                    result[key] = None
            else:
                result[field] = None
            schema_idx += 1
        
        return result

    def _map_value_list_to_object(self, values: List[Any], schema: Schema) -> Dict[str, Any]:
        """Value definition list'ini schema'ya göre object'e dönüştürür"""
        result: Dict[str, Any] = {}
        for idx, field in enumerate(schema):
            # Eksik değer gelirse None
            value = values[idx] if idx < len(values) else None

            if isinstance(field, tuple):
                key, sub_t = field
                # Alt tip için value'yu Node olarak sarmalayıp build'e geç
                value_node = Node("primitive", value)
                result[key] = self.build(value_node, sub_t)
            else:
                # Basit alan
                result[field] = value
        return result


# ---- Dış API ----

def parse_bref(content: str):
    # 1) Tip tanımlarını ve value definition'ları al, kalan veri gövdesini tut
    type_defs, value_defs, data_text = parse_type_definitions(content)

    # 2) AST'e parse et
    parser = Parser(data_text)
    root = parser.parse_value()
    # (Kökten sonra anlamsız artıkları kabul etmiyoruz ama
    #  sadece boşluk varsa sorun değil)
    parser.skip_ws()
    # 3) AST'i JSON'a dönüştür (şemaları uygulayarak)
    mat = Materializer(type_defs, value_defs)
    return mat.build(root, None)
