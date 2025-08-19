"""
Array testleri - dizi tipleri
"""
from tests.helpers import run_test

def test_array_type():
    run_test(
        "6_array_type.bref",
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

"""
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
    )"""