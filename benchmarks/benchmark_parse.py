from pathlib import Path
import json
import timeit
import brefpy


def benchmark_bref():
    content = Path(__file__).parent / "data.bref"
    data = content.read_text(encoding="utf-8")
    brefpy.parse(data)

def benchmark_json():
    content = Path(__file__).parent / "output.json"
    data = content.read_text(encoding="utf-8")
    json.loads(data)


def main():
    repeat = 10
    number = 2

    bref_time = timeit.repeat(benchmark_bref, repeat=repeat, number=number)
    json_time = timeit.repeat(benchmark_json, repeat=repeat, number=number)

    bref_min = min(bref_time) / number
    json_min = min(json_time) / number

    print("=== Benchmark Results ===")
    print(f"Number: {number}", f"Repeat: {repeat}")
    print(f"Bref parse (min per run): {bref_min:.8f} s")
    print(f"JSON parse (min per run): {json_min:.8f} s")

    factor = bref_min / json_min
    print(f"=> JSON parse is {factor:.2f}x faster")


if __name__ == "__main__":
    main()
