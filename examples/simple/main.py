from pathlib import Path
import bref

def main():
    bref_path = Path(__file__).parent / "data.bref"
    content = bref_path.read_text(encoding="utf-8")
    result = bref.parse(content)
    print(result[0]['album']['tracks'][0]['title'])

if __name__ == "__main__":
    main()
