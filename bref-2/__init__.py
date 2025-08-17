from .converter import parse_bref

def toJSON(content: str):
    return parse_bref(content)
