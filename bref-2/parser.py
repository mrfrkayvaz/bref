from typing import List, Optional, Union

from .ast import Node, ParseError
from .utils import Schema, parse_schema_fields


class Parser:
    def __init__(self, text: str):
        self.s = text
        self.i = 0
        self.n = len(text)

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
        if ch == '-' or ch.isdigit():
            return Node("primitive", self.parse_number())
        ident = self.try_parse_identifier_literal()
        if ident == "null":
            return Node("primitive", None)
        if ident is not None:
            return Node("primitive", ident)
        if ch == '.':
            self.get()
            return Node("default", None)
        
        if ch.isalpha() or ch == '_':
            return Node("primitive", self.read_identifier())

        raise ParseError(f"Beklenmeyen karakter: {ch} @ {self.i}")

    def parse_list_node(self) -> Node:
        assert self.get() == '{'
        items: List[Node] = []
        self.skip_ws()
        if self.peek() == '}':
            self.get()
            type_ann = self.parse_type_annotation()
            return Node("list", items, type_ann)

        while True:
            if self.peek().isalpha() or self.peek() == '_':
                start_pos = self.i
                key = self.read_identifier()
                self.skip_ws()
                
                if self.peek() == ':':
                    self.get()
                    self.skip_ws()
                    value = self.parse_value()
                    items.append(Node("key_value", (key, value)))
                else:
                    self.i = start_pos
                    items.append(self.parse_value())
            else:
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
        self.skip_ws()
        if self.eof() or self.peek() != ':':
            return None
        self.get()
        self.skip_ws()
        ch = self.peek()
        if ch == '{':
            schema_text = self.read_braced()
            return parse_schema_fields(schema_text)
        name = self.read_identifier()
        return name

    def parse_string(self) -> str:
        assert self.get() == '"'
        buf = ['"']
        while not self.eof():
            c = self.get()
            buf.append(c)
            if c == '\\':
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
                self._skip_string_inside('"')
        raise ParseError("Kapanmayan '{'")

    def _skip_string_inside(self, quote: str):
        while not self.eof():
            c = self.get()
            if c == '\\':
                if not self.eof():
                    self.get()
                continue
            if c == quote:
                break
