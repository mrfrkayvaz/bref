import json
from pathlib import Path
import brefpy
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def run_test(file_name, expected):
    file_path = Path(__file__).parent / "data" / file_name
    content = file_path.read_text(encoding="utf-8")
    result = brefpy.toJSON(content)

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
        "1_simple_type.bref",
        {
            "title": "Bohemian Rhapsody",
            "duration": "5:55",
            "streams": 1980000000,
            "is_favorite": True
        }
    )

def test_nested_type():
    run_test(
        "2_nested_type.bref",
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
        "3_array_type.bref",
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
                "is_favorite": True
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
                "is_favorite": True
            }
        ]
    )

def test_value_definitions():
    run_test(
        "4_value_definitions.bref",
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

def test_all_data_types():
    """Tüm JSON veri tiplerini test eder: string, boolean, null, integer, float, object, array"""
    run_test(
        "5_all_data_types.bref",
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
        "6_default_values.bref",
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

def test_inline_type():
    run_test(
        "7_inline_type.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55"
            }
        ]
    )

def test_key_value_pairs():
    """Key-value pairs özelliğini test eder"""
    run_test(
        "8_key_value_pairs.bref",
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

def test_nested_inline_schema():
    run_test(
        "9_nested_inline_schema.bref",
        [
            {
                "title": "Kitap Dünyası",
                "test": {
                    "age": 123
                }
            }
        ]
    )

def test_type_definition_mismatch():
    """Type definition mismatch senaryosunu test eder - key-value ve positional data karışımı"""
    run_test(
        "10_type_definition_mismatch.bref",
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
                "is_favorite": True
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
                "is_favorite": True
            },
            {
                "release_date": "1973-03-01",
                "awards": ["Grammy Hall of Fame", "UK Music Hall of Fame"],
                "producer": "Roy Thomas Baker"
            }
        ]
    )

def test_default_value_end():
    """Default value end senaryosunu test eder - son field için default değer"""
    run_test(
        "11_default_value_end.bref",
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
            }
        ]
    )

def test_default_value_middle():
    """Default value middle senaryosunu test eder - ortadaki field'lar için default değer"""
    run_test(
        "12_default_value_middle.bref",
        [
            {
                "name": "John Doe",
                "age": 25,
                "city": "Unknown",
                "address": {
                    "street": "Main St",
                    "postal_code": "12345"
                },
                "is_active": True
            }
        ]
    )

def test_type_definition_mismatch_inline():
    """Type definition mismatch inline senaryosunu test eder - farklı type'lar için inline schema"""
    run_test(
        "13_type_definition_mismatch_inline.bref",
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
                "is_favorite": True
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
                "is_favorite": True
            },
            {
                "release_date": "1973-03-01",
                "awards": ["Grammy Hall of Fame", "UK Music Hall of Fame"],
                "producer": "Roy Thomas Baker"
            }
        ]
    )

def test_missing_data_end():
    """Missing data end senaryosunu test eder - son field'lar eksik, default yoksa eklenmez"""
    run_test(
        "14_missing_data_end.bref",
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
                "is_favorite": True
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
                }
            }
        ]
    )


def test_missing_album_data():
    """Missing album data senaryosunu test eder - album verisi eksik, default yoksa eklenmez"""
    run_test(
        "15_missing_album_data.bref",
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
                "is_favorite": True
            },
            {
                "title": "Smells Like Teen Spirit",
                "duration": "5:01",
                "genre": "Alternative Rock"
            }
        ]
    )


def test_nested_defaults():
    """Nested defaults senaryosunu test eder - nested type'larda default değerler"""
    run_test(
        "16_nested_defaults.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55",
                "genre": "Rock",
                "album": {
                    "title": "test",
                    "year": 1975,
                    "band": {
                        "name": "band default",
                        "country": "UK"
                    }
                },
                "streams": 1980000000,
                "is_favorite": True
            },
            {
                "title": "Smells Like Teen Spirit",
                "duration": "5:01",
                "genre": "Alternative Rock",
                "album": {
                    "title": "test",
                    "band": {
                        "name": "band default"
                    }
                }
            }
        ]
    )


def test_mixed_defaults():
    """Mixed defaults senaryosunu test eder - bazı field'larda default, bazılarında veri"""
    run_test(
        "17_mixed_defaults.bref",
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
                "is_favorite": True
            },
            {
                "title": "Smells Like Teen Spirit",
                "duration": "5:01",
                "genre": "Alternative Rock",
                "album": {
                    "title": "test",
                    "year": 2020,
                    "band": {
                        "name": "band default"
                    }
                },
                "streams": 300000,
                "is_favorite": False
            }
        ]
    )
