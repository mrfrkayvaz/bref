from pathlib import Path
import brefpy

def main():
    bref_path = Path(__file__).parent / "data.bref"
    content = bref_path.read_text(encoding="utf-8")
    
    try:
        result = brefpy.parse(content)
        print(result["data"])
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
