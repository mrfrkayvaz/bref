from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Union

from .utils import Schema


@dataclass
class Node:
    kind: str
    value: Any
    type_ann: Optional[Union[str, Schema]] = None


class ParseError(Exception):
    pass
