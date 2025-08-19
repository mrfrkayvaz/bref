"""
Nested type testleri - iç içe objeler
"""
from tests.helpers import run_test

def test_nested_type():
    run_test(
        "4_nested_type.bref",
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

def test_nested_inline_schema():
    run_test(
        "5_nested_inline_schema.bref",
        [
            {
                "title": "Kitap Dünyası",
                "test": {
                    "age": 123
                }
            }
        ]
    )

"""
def test_nested_defaults():
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
"""