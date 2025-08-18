# Bref Python Parser

This document describes the development of a Python parser for the Bref data format.
The parser should read data in Bref format and produce standard Python structures: arrays are converted into lists, and objects are converted into dictionaries.
To help you understand the Bref format, I provide the corresponding JSON representations under the code examples.

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

If you want to define an array inside an object, you can specify it like this:

**Bref**

```json
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band, tracks:track[] } 
:band { name, country }
:track { title }
 
[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { 
      "A Night at the Opera", 1975, { "Queen", "UK" }, 
      [ { "Love of My Life" }, { "You're My Best Friend" } ] 
    },
    1980000000, true
  }
]: song
```

### Full JSON data type support

Bref supports all JSON-compatible data types: booleans (`true`, `false`), null values, strings, integers, floats, objects, and arrays. This ensures any JSON data can be represented in Bref.

**Bref**

```json
:person { name, age, height, is_active, email, preferences:preferences, scores }
:preferences { theme, language }

[
  { "John Doe", 30, 175.5, true, null, { "dark", "en" }, [ 85, 92, 78 ] },
  { "Jane Smith", 25, 162.0, false, "jane@example.com", { "light", "tr" }, [ 95, 88, 91 ] },
  { "Bob Wilson", 35, 180.2, true, null, { "auto", "de" }, [ 72, 85, 90 ] }
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

### Missing data

For missing values, no special symbol is used. Instead, fields are simply skipped by leaving consecutive commas. This means `,,` indicates that some fields are absent.

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

## Project Structure

The bref folder will be our working directory. Inside this folder, all operations will start from converter.py.

There will be two main functions defined here:

parse: this function converts a Bref string into Python dict and list objects.

toJSON: this function will remain empty for now.

toBREF: this function will remain empty for now.

## Tasks

You will go through these tasks step by step. I will assign a number to each task. Your job is to carefully understand the task, ask questions if anything is unclear, and if you are completely confident, proceed to implement it. Perform these implementations using Python.

### Task 1

The first task is to implement logic in the toJSON function that identifies three key components from the incoming Bref data:

type_defs – stores all type definitions.

At this stage, we are not processing actual data objects yet. The parser should first analyze type definitions before moving on to the data.

**Bref**
```json
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band, tracks:track[] }
:track { title, duration, genre }
:band { name, country }
```

**Python**
```python
type_defs = {
  "song": ["title", "duration", "genre", ("album", "album", FieldType.OBJECT), "streams", "is_favorite"],
  "album": ["title", "year", ("band", "band"), ("tracks", "track", FieldType.ARRAY)],
  "band": ["name", "country"]
}
```

### Task 2

In this task, our goal is to process the data using the type_defs definitions.

When writing the code, make sure files do not become too long. If necessary, create new files. Each file should only contain functions related to its filename.

The main logic is as follows:

 - There should not be any item without a key definition. If such a case exists, the parser must raise an error.

 - If the data is an object, the output should be a Python dict.

 - If the data is an array, the output should be a Python list.

**Bref**

```json
:song { title, duration, genre, album:album, streams, is_favorite }
:album { title, year, band:band, tracks:track[] }
:band { name, country }
:track { title }

[
  {
    "Bohemian Rhapsody", "5:55", "Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" }, [{"track 1"}, {"track 2"}] },
    1980000000, true
  },
  {
    "Smells Like Teen Spirit", "5:01", "Alternative Rock",
    { "A Night at the Opera", 1975, { "Queen", "UK" }, [{"track 1"}, {"track 2"}] },
    300000, false
  }
]: song
```

```python
[
  {
    "title": "Bohemian Rhapsody",
    "duration": "5:55",
    "genre": "Rock",
    "album": {
      "title": "A Night at the Opera",
      "year": 1975,
      "band": {
        "title": "Queen",
        "country": "UK"
      },
      "tracks": [
        {"title": "track 1"},
        {"title": "track 2"}
      ]
    },
    "streams": 1980000000,
    "is_favorite": True
  },
  {
    "title": "Smells Like Teen Spirit",
    "duration": "5:01",
    "genre": "Alternative Rock",
    "album": {
      "title": "A Night at the Opera",
      "year": 1975,
      "band": {
        "title": "Queen",
        "country": "UK"
      },
      "tracks": [
        {"title": "track 1"},
        {"title": "track 2"}
      ]
    },
    "streams": 300000,
    "is_favorite": False
  }
]
```

### Task 3

Our `parse` function already converts a given Bref string into Python data structures (`dict` / `list`).  

Now the goal is to update the implementation of `bref.toJSON`.  

- The incoming Bref string should first be passed through the `parse` function.  
- Then, the resulting Python structure should be converted into a JSON string (using `json.dumps`).  

In short: **Bref string → `parse()` → Python dict/list → JSON string**.
