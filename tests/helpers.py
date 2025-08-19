"""
Test yardımcı fonksiyonları
"""
import json
from pathlib import Path
import brefpy
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def run_test(file_name, expected):
    """
    Bref dosyasını test eder
    
    Args:
        file_name: Test edilecek .bref dosyasının adı
        expected: Beklenen JSON çıktısı
    """
    file_path = Path(__file__).parent / "data" / file_name
    content = file_path.read_text(encoding="utf-8")
    
    try:
        result = brefpy.to_json(content)
        result_parsed = json.loads(result)
    except Exception as e:
        console.print(f"[bold red]{file_name} - Parse Error: {e}[/bold red]")
        raise

    if result_parsed != expected:
        console.print(f"[bold red]{file_name} failed[/bold red]")
        console.print("[bold yellow]Got:[/bold yellow]")
        console.print(Syntax(json.dumps(result_parsed, indent=2, ensure_ascii=False, sort_keys=True), "json"))
        console.print("[bold yellow]Expected:[/bold yellow]")
        console.print(Syntax(json.dumps(expected, indent=2, ensure_ascii=False, sort_keys=True), "json"))
        raise AssertionError(f"{file_name} failed")
    else:
        console.print(f"[bold green]{file_name} passed[/bold green]")


def compare_json(result, expected, test_name):
    """JSON karşılaştırması yapar"""
    if result != expected:
        console.print(f"[bold red]{test_name} failed[/bold red]")
        console.print("[bold yellow]Result:[/bold yellow]")
        console.print(Syntax(json.dumps(result, indent=2, ensure_ascii=False), "json"))
        console.print("[bold yellow]Expected:[/bold yellow]")
        console.print(Syntax(json.dumps(expected, indent=2, ensure_ascii=False), "json"))
        return False
    return True
