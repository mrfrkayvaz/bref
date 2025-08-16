import json
from pathlib import Path
import bref

def main():
    bref_path = Path(__file__).parent / "data.bref"
    content = bref_path.read_text(encoding="utf-8")
    result = bref.toJSON(content)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
