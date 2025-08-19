"""
Temel tip testleri - simple types, primitive values
"""
from pathlib import Path
from tests.helpers import run_test


def test_simple_type():
    """Basit tip tanımı testi"""
    run_test(
        "1_simple_type.bref",
        {
            "title": "Bohemian Rhapsody",
            "duration": "5:55",
            "streams": 1980000000,
            "is_favorite": True
        }
    )

def test_inline_type():
    run_test(
        "2_inline_type.bref",
        [
            {
                "title": "Bohemian Rhapsody",
                "duration": "5:55"
            }
        ]
    )

def test_all_data_types():
    run_test(
        "3_all_data_types.bref",
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