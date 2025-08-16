import json
from pathlib import Path
import bref
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def run_test(file_name, expected):
    file_path = Path(__file__).parent / "data" / file_name
    content = file_path.read_text(encoding="utf-8")
    result = bref.toJSON(content)

    if result != expected:
        console.print(f"[bold red]{file_name} failed[/bold red]")
        console.print("[bold yellow]Got:[/bold yellow]")
        console.print(Syntax(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), "json"))
        console.print("[bold yellow]Expected:[/bold yellow]")
        console.print(Syntax(json.dumps(expected, indent=2, ensure_ascii=False, sort_keys=True), "json"))
        raise AssertionError(f"{file_name} failed")
    else:
        console.print(f"[bold green]{file_name} passed[/bold green]")

def test_simple():
    run_test(
        "simple.bref",
        {
            "title": "Bohemian Rhapsody",
            "duration": "5:55",
            "genre": "Rock",
            "album": {
                "title": "A Night at the Opera",
                "year": 1975,
                "artist": {
                    "name": "Queen",
                    "country": "UK"
                }
            },
            "streams": 1980000000,
            "is_favorite": True
        }
    )

def test_array():
    run_test(
        "array.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55"
            },
            {
                "title": "Wonderwall",
                "duration": "4:18"
            }
        ]
    )

def test_inline_type():
    run_test(
        "inline_type.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55"
            }
        ]
    )

def test_nested_array():
    run_test(
        "nested_array.bref",
        {
            "title": "A Night at the Opera",
            "year": 1975,
            "artists": [
                {"name": "Freddie Mercury", "country": "UK"},
                {"name": "Brian May", "country": "UK"}
            ]
        }
    )

def test_value_definitions():
    run_test(
        "value_definitions.bref",
        [
            {
                "name": "TeknoMarket",
                "address": {"country": "Türkiye", "city": "Istanbul", "town": "Maltepe"}
            },
            {
                "name": "Kitap Dünyası",
                "address": {"country": "Türkiye", "city": "Istanbul", "town": "Maltepe"}
            },
            {
                "name": "Lezzet Durağı",
                "address": {"country": "Türkiye", "city": "Ankara", "town": "Beypazarı"}
            },
            {
                "name": "Moda Giyim",
                "address": {"country": "Türkiye", "city": "Ankara", "town": "Beypazarı"}
            }
        ]
    )

def test_nested_inline_schema():
    run_test(
        "nested_inline_schema.bref",
        [
            {
                "title": "Kitap Dünyası",
                "test": {
                    "age": 123
                }
            }
        ]
    )

def test_all_data_types():
    """Tüm JSON veri tiplerini test eder: string, boolean, null, integer, float, object, array"""
    run_test(
        "all_data_types.bref",
        [
            {
                "name": "John Doe",
                "age": 30,
                "height": 175.5,
                "is_active": True,
                "email": None,
                "preferences": {
                    "theme": "dark",
                    "language": "en"
                },
                "scores": [85, 92, 78]
            },
            {
                "name": "Jane Smith",
                "age": 25,
                "height": 162.0,
                "is_active": False,
                "email": "jane@example.com",
                "preferences": {
                    "theme": "light",
                    "language": "tr"
                },
                "scores": [95, 88, 91]
            },
            {
                "name": "Bob Wilson",
                "age": 35,
                "height": 180.2,
                "is_active": True,
                "email": None,
                "preferences": {
                    "theme": "auto",
                    "language": "de"
                },
                "scores": [72, 85, 90]
            }
        ]
    )

def test_default_values():
    """Default values özelliğini test eder"""
    run_test(
        "default_values.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55",
                "genre": "Rock",
                "album": {
                    "title": "A Night at the Opera",
                    "year": 1975,
                    "band": {
                        "name": "Queen",
                        "country": "UK"
                    }
                },
                "streams": 1980000000,
                "is_favorite": False
            },
            {
                "title": "Smells Like Teen Spirit",
                "duration": "5:01",
                "genre": "Alternative Rock",
                "album": {
                    "title": "Nevermind",
                    "year": 1991,
                    "band": {
                        "name": "Nirvana",
                        "country": "USA"
                    }
                },
                "streams": 1750000000,
                "is_favorite": False
            }
        ]
    )

def test_key_value_pairs():
    """Key-value pairs özelliğini test eder"""
    run_test(
        "key_value_pairs.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55",
                "genre": "Rock",
                "album": {
                    "title": "A Night at the Opera",
                    "year": 1975,
                    "band": {
                        "name": "Queen",
                        "country": "UK"
                    }
                },
                "streams": 1980000000,
                "is_favorite": True,
                "mood": "Epic",
                "rating": 5
            },
            {
                "title": "Smells Like Teen Spirit",
                "duration": "5:01",
                "genre": "Alternative Rock",
                "album": {
                    "title": "Nevermind",
                    "year": 1991,
                    "band": {
                        "name": "Nirvana",
                        "country": "USA"
                    }
                },
                "streams": 1750000000,
                "is_favorite": False,
                "mood": "Angry",
                "rating": 4
            }
        ]
    )
