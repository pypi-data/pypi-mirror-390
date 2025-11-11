# gspread_datarame

Simple data utilities for working with spreadsheet data.

## Installation

```bash
pip install gspread_datarame
```

## Usage

```python
import gspread_datarame

# Convert data to dictionary format
data = {"name": "John", "age": 30}
converted = gspread_datarame.to_dataframe(data)

# Convert back
original = gspread_datarame.from_dataframe(converted)

# Get version
print(gspread_datarame.get_version())
```

## Features

- Simple data conversion utilities
- Lightweight with no dependencies
- Easy to use API

## License

MIT License
