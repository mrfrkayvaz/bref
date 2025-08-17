from .utils import parse_type_definitions
from .parser import Parser
from .materializer import Materializer


def parse_bref(content: str):
    type_defs, value_defs, data_text = parse_type_definitions(content)

    print(type_defs)
    print(value_defs)

    #parser = Parser(data_text)
    #root = parser.parse_value()
    #parser.skip_ws()

    #mat = Materializer(type_defs, value_defs)
    #return mat.build(root, None)
