from typing import Any, List, Optional, Union, Dict

from .ast import Node, ParseError
from .utils import Schema

class Materializer:
    def __init__(self, type_defs: Dict[str, Schema], value_defs: Dict[str, List[Any]]):
        self.type_defs = type_defs
        self.value_defs = value_defs

    def build(self, node: Node, expected_type: Optional[Union[str, Schema]] = None) -> Any:
        effective_type = node.type_ann if node.type_ann is not None else expected_type

        if node.kind == "primitive":
            if isinstance(node.value, str) and node.value in self.value_defs:
                value_list = self.value_defs[node.value]
                if expected_type is not None:
                    schema = self._resolve_schema(expected_type)
                    return self._map_value_list_to_object(value_list, schema)
                return value_list
            return node.value

        if node.kind == "array":
            if effective_type is not None:
                return [self.build(child, effective_type) for child in node.value]
            return [self.build(child, None) for child in node.value]

        if node.kind == "list":
            if effective_type is None:
                return [self.build(child, None) for child in node.value]
            schema = self._resolve_schema(effective_type)
            return self._map_list_to_object(node.value, schema)

        raise ParseError("Bilinmeyen düğüm türü")

    def _resolve_schema(self, t: Union[str, Schema]) -> Schema:
        if isinstance(t, list):
            return t
        if t not in self.type_defs:
            raise ParseError(f"Tanımsız tip: {t}")
        return self.type_defs[t]

    def _map_list_to_object(self, items: List[Node], schema: Schema) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        
        key_value_items = [item for item in items if item.kind == "key_value"]
        positional_items = [item for item in items if item.kind != "key_value"]
        
        if key_value_items and not positional_items:
            for item in key_value_items:
                key, value_node = item.value
                result[key] = self.build(value_node, None)
            return result
        
        for item in key_value_items:
            key, value_node = item.value
            result[key] = self.build(value_node, None)
        
        schema_idx = 0
        
        for item in positional_items:
            if schema_idx < len(schema):
                field = schema[schema_idx]
                if (isinstance(item, Node) and 
                    item.kind == "default"):
                    if isinstance(field, tuple):
                        key, sub_t = field
                        if isinstance(sub_t, (bool, int, float, type(None))):
                            result[key] = sub_t
                        elif isinstance(sub_t, str):
                            if sub_t in self.type_defs:
                                sub_result = self._create_default_object(sub_t)
                                if sub_result:
                                    result[key] = sub_result
                            else:
                                result[key] = sub_t
                        else:
                            result[key] = None
                    else:
                        result[field] = None
                else:
                    if isinstance(field, tuple):
                        key, sub_t = field
                        if isinstance(sub_t, (bool, int, float, type(None))):
                            result[key] = sub_t
                        elif isinstance(sub_t, str):
                            if sub_t in self.type_defs:
                                result[key] = self.build(item, sub_t)
                            else:
                                result[key] = sub_t
                        else:
                            result[key] = self.build(item, sub_t)
                    else:
                        result[field] = self.build(item, None)
                schema_idx += 1
        
        while schema_idx < len(schema):
            field = schema[schema_idx]
            if isinstance(field, tuple):
                key, sub_t = field
                if isinstance(sub_t, (bool, int, float, type(None))):
                    result[key] = sub_t
                elif isinstance(sub_t, str):
                    if sub_t in self.type_defs:
                        pass
                    else:
                        result[key] = sub_t
            else:
                pass
            schema_idx += 1
        
        for field in schema:
            if isinstance(field, tuple):
                key, sub_t = field
                if key not in result:
                    if isinstance(sub_t, (bool, int, float, type(None))):
                        result[key] = sub_t
                    elif isinstance(sub_t, str):
                        if sub_t in self.type_defs:
                            sub_result = self._create_default_object(sub_t)
                            if sub_result:
                                result[key] = sub_result
                        else:
                            result[key] = sub_t
        
        return result

    def _create_default_object(self, type_name: str) -> Optional[Dict[str, Any]]:
        if type_name not in self.type_defs:
            return None
            
        schema = self.type_defs[type_name]
        result = {}
        
        for field in schema:
            if isinstance(field, tuple):
                key, sub_t = field
                if isinstance(sub_t, (bool, int, float, type(None))):
                    result[key] = sub_t
                elif isinstance(sub_t, str):
                    if sub_t in self.type_defs:
                        nested_result = self._create_default_object(sub_t)
                        if nested_result:
                            result[key] = nested_result
                    else:
                        result[key] = sub_t
            else:
                pass
        
        return result if result else None

    def _map_value_list_to_object(self, values: List[Any], schema: Schema) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for idx, field in enumerate(schema):
            value = values[idx] if idx < len(values) else None

            if isinstance(field, tuple):
                key, sub_t = field
                if value is not None:
                    value_node = Node("primitive", value)
                    result[key] = self.build(value_node, sub_t)
            else:
                if value is not None:
                    result[field] = value
        return result
