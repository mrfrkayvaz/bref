"""
Invalid data testleri - karmaşık ve edge case senaryolar
"""
from tests.helpers import run_test


def test_key_value_pairs():
    run_test(
        "7_key_value_pairs.bref",
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

def test_type_definition_mismatch():
    run_test(
        "8_type_definition_mismatch.bref",
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


def test_type_definition_mismatch_inline():
    run_test(
        "9_type_definition_mismatch_inline.bref",
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
