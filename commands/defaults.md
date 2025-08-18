### Default values

Bref allows defining default values for type fields. These defaults are applied when the value is omitted in the data object.

* For **scalars** (strings, numbers, booleans, null), defaults are declared explicitly, e.g. `title: "default title"` or `is_active: false`.
* For **objects**, defaults are not defined inline at the field level. Instead, you specify the type (`album: album`) and the defaults come from the nested type’s definition. This ensures consistency across nested structures.
* When using defaults inside data objects, the special `.` placeholder is used. This indicates that the default value for that field should be applied.

**Bref**

```json
:song { title, duration, genre, album:album, streams: 20000, is_favorite: false }
:album { title: "default album title", year, band:band }
:band { name: "default band name", country }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" } },  
    1980000000, .
  },
  {
    "Smells Like Teen Spirit", "5:01", "Alternative Rock",
    ., ., .
  }
]: song
```

**JSON**

```json
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
    "is_favorite": false
  },
  {
    "title": "Smells Like Teen Spirit",
    "duration": "5:01",
    "genre": "Alternative Rock",
    "album": {
      "title": "default album title",
      "band": {
        "name": "default band name"
      }
    },
    "streams": 20000,
    "is_favorite": false
  }
]
```