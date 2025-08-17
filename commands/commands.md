# Bref Python Parser

This document describes the development of a Python parser for the Bref data format.
The parser should read data in Bref format and produce standard JSON output.

## Goals

The parser should support the following scenarios:

### Type definitions

In Bref, you can append a type label such as `: song` at the end of an object.
In this case, the parser assumes the type `song` has been defined earlier and maps the values to the corresponding keys.

**Bref**

```json
{ "Bohemian Rhapsody", "5:55", 1980000000, true }: song
```

**JSON**

```json
{
  "title": "Bohemian Rhapsody",
  "duration": "5:55",
  "streams": 1980000000,
  "is_favorite": true
}
```

### Inline type definitions

If a type is not predefined, you can directly write the schema as `: { ... }` at the end of the object.
This allows mapping without requiring a prior type declaration.

**Bref**

```json
{ "Bohemian Rhapsody", "5:55", 1980000000, true }: { title, duration, streams, is_favorite }
```

**JSON**

```json
{
  "title": "Bohemian Rhapsody",
  "duration": "5:55",
  "streams": 1980000000,
  "is_favorite": true
}
```

### Nested type definitions

Types can be nested within one another. For example, a `song` contains an `album`, and the `album` contains an `artist`. This structure maps naturally to JSON.

**Bref**

```json
:artist { name, country }
:album { title, year, artist:artist }
:song { title, duration, genre, album:album, streams, is_favorite }

{ "Bohemian Rhapsody", "5:55", "Rock", { "A Night at the Opera", 1975, { "Queen", "UK" } }, 1980000000, true }: song
```

**JSON**

```json
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
  "is_favorite": true
}
```

### Array type definitions

Multiple objects can be grouped into an array using square brackets. A type label such as `: song` can then be applied to all elements.

**Bref**

```json
[
  { "Bohemian Rhapsody", "5:55", "Rock", { "A Night at the Opera", 1975, { "Queen", "UK" } }, 1980000000, true },
  { "Smells Like Teen Spirit", "5:01", "Alternative Rock", { "Nevermind", 1991, { "Nirvana", "USA" } }, 1750000000, true }
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
      "artist": {
        "name": "Queen",
        "country": "UK"
      }
    },
    "streams": 1980000000,
    "is_favorite": true
  },
  {
    "title": "Smells Like Teen Spirit",
    "duration": "5:01",
    "genre": "Alternative Rock",
    "album": {
      "title": "Nevermind",
      "year": 1991,
      "artist": {
        "name": "Nirvana",
        "country": "USA"
      }
    },
    "streams": 1750000000,
    "is_favorite": true
  }
]
```

### Value definitions

Bref also supports defining reusable values, which can then be referenced multiple times. This helps avoid repetition.

**Bref**

```json
:store { name, address:address }
:address { country, city, town }

:ist { "Türkiye", "Istanbul", "Maltepe" }
:ank { "Türkiye", "Ankara", "Beypazarı" }

[
  { "TeknoMarket", ist },
  { "Kitap Dünyası", ist },
  { "Lezzet Durağı", ank },
  { "Moda Giyim", ank }
]: store
```

**JSON**

```json
[
  {
    "name": "TeknoMarket",
    "address": {
      "country": "Türkiye",
      "city": "Istanbul",
      "town": "Maltepe"
    }
  },
  {
    "name": "Kitap Dünyası",
    "address": {
      "country": "Türkiye",
      "city": "Istanbul",
      "town": "Maltepe"
    }
  },
  {
    "name": "Lezzet Durağı",
    "address": {
      "country": "Türkiye",
      "city": "Ankara",
      "town": "Beypazarı"
    }
  },
  {
    "name": "Moda Giyim",
    "address": {
      "country": "Türkiye",
      "city": "Ankara",
      "town": "Beypazarı"
    }
  }
]
```

### Full JSON data type support

Bref supports all JSON-compatible data types: booleans (`true`, `false`), null values, strings, integers, floats, objects, and arrays. This ensures any JSON data can be represented in Bref.

**Bref**

```json
:person { name, age, height, is_active, email, preferences, scores }
:preferences { theme, language }

[
  { "John Doe", 30, 175.5, true, null, { "dark", "en" }: preferences, [ 85, 92, 78 ] },
  { "Jane Smith", 25, 162.0, false, "jane@example.com", { "light", "tr" }: preferences, [ 95, 88, 91 ] },
  { "Bob Wilson", 35, 180.2, true, null, { "auto", "de" }: preferences, [ 72, 85, 90 ] }
]: person
```

**JSON**

```json
[
  {
    "name": "John Doe",
    "age": 30,
    "height": 175.5,
    "is_active": true,
    "email": null,
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
    "is_active": false,
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
    "is_active": true,
    "email": null,
    "preferences": {
      "theme": "auto",
      "language": "de"
    },
    "scores": [72, 85, 90]
  }
]
```

### Type definition mismatch

Bref also allows mixing structured type-based objects with full JSON-style objects. If you provide an inline JSON object, you must include **all required keys explicitly**. This gives flexibility to embed raw JSON when needed.

**Bref**

```json
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band }
:band { name, country }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" } },  
    1980000000, true
  },
  {
    release_date: "1973-03-01",
    awards: ["Grammy Hall of Fame", "UK Music Hall of Fame"],
    producer: "Roy Thomas Baker"
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
    "is_favorite": true
  },
  {
    "release_date": "1973-03-01",
    "awards": ["Grammy Hall of Fame", "UK Music Hall of Fame"],
    "producer": "Roy Thomas Baker"
  }
]
```

This demonstrates that you can switch to pure JSON-style objects inside arrays or collections, but in such cases you are responsible for specifying every field explicitly.

---

You can also inline override the array’s declared type by providing a different type mapping for specific objects. This allows mixing multiple type definitions within the same array.

**Bref**

```json
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band }
:band { name, country }
:special_song { release_date, awards, producer }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" } },  
    1980000000, true
  },
  {
    "Smells Like Teen Spirit", "5:01", "Alternative Rock",
    { "Nevermind", 1991, { "Nirvana", "USA" } },
    1750000000, true
  },
  {
    "1973-03-01", ["Grammy Hall of Fame", "UK Music Hall of Fame"], "Roy Thomas Baker"
  }: special_song
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
    "is_favorite": true
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
    "is_favorite": true
  },
  {
    "release_date": "1973-03-01",
    "awards": ["Grammy Hall of Fame", "UK Music Hall of Fame"],
    "producer": "Roy Thomas Baker"
  }
]
```

This shows that even when the array is declared with `: song`, you can override specific entries with another type like `special_song`. This provides flexibility for heterogeneous arrays.

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

### Missing data

For missing values, no special symbol is used. Instead, fields are simply skipped by leaving consecutive commas. This means `,,` indicates that some fields are absent and should not be filled with defaults.

**Bref**

```json
:song { title, duration, genre, album:album, streams, is_favorite }

[
  { "Bohemian Rhapsody", , "Rock", , 1980000000, true },
  { "Unknown Song", , , , , false }
]: song
```

**JSON**

```json
[
  {
    "title": "Bohemian Rhapsody",
    "genre": "Rock",
    "streams": 1980000000,
    "is_favorite": true
  },
  {
    "title": "Unknown Song",
    "is_favorite": false
  }
]
```
