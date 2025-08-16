import pytest
from bref.converter import parse_bref


def test_type_references_not_default_values():
    """Test that type references like album:album are not treated as default values"""
    content = """
:song { title, duration, genre, album:album, streams, is_favorite: false }
:album { title, year, band:band }
:band { name, country }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" } },  
    1980000000, .
  }
]: song
"""
    
    result = parse_bref(content)
    song = result[0]

    print(song)
    
    # album field'ı album tipinde olmalı, default değer olmamalı
    assert "album" in song
    assert isinstance(song["album"], dict)
    assert "title" in song["album"]
    assert "year" in song["album"]
    assert "band" in song["album"]
    
    # is_favorite default değeri false olmalı
    assert "is_favorite" in song
    assert song["is_favorite"] == False


def test_mixed_default_values_and_type_references():
    """Test mixing default values and type references in schema"""
    content = """
:person { name, age: 25, city: "Unknown", address:address, is_active: true }
:address { street, postal_code }

[
  {
    "John Doe", .,.,
    { "Main St", "12345" }
  }
]: person
"""
    
    result = parse_bref(content)
    person = result[0]
    
    # name: positional value
    assert "name" in person
    assert person["name"] == "John Doe"
    
    # age: default value 25 (hiç değer verilmemiş)
    assert "age" in person
    assert person["age"] == 25
    
    # city: default value "Unknown" (hiç değer verilmemiş)
    assert "city" in person
    assert person["city"] == "Unknown"
    
    # address: type reference (değer verilmiş)
    assert "address" in person
    assert isinstance(person["address"], dict)
    assert "street" in person["address"]
    assert "postal_code" in person["address"]
    
    # is_active: default value true (hiç değer verilmemiş)
    assert "is_active" in person
    assert person["is_active"] == True
