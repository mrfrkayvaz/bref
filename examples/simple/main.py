import json
from pathlib import Path
import bref

def main():
    bref_path = Path(__file__).parent / "data.bref"
    content = bref_path.read_text(encoding="utf-8")
    result = bref.toJSON(content)
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    
    '''
    output_path = Path(__file__).parent / "data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"JSON dosyası oluşturuldu: {output_path}")
    
    bref_size = bref_path.stat().st_size
    json_size = output_path.stat().st_size
    
    print(f"\nDosya boyutları:")
    print(f"data.bref: {bref_size:,} bytes")
    print(f"data.json: {json_size:,} bytes")
    print(f"Boyut oranı: {json_size / bref_size:.2f}x")
    '''

if __name__ == "__main__":
    main()
