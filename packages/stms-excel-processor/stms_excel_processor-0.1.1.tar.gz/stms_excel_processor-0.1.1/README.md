# Excel Processor

A lightweight Excel Processor.

## Installation

```bash
pip install stms-excel-processor
```

## Usage

Instead of:
Use:
```python
from excel_processor import Workbook, FileFormat
```

### Example

```python
from excel_processor import Workbook, FileFormat

# Load Excel file
workbook = Workbook()
workbook.LoadFromFile("input.xlsx")

# Process your data...

# Save Excel file
workbook.SaveToFile("output.xlsx", FileFormat.Version2016)
workbook.Dispose()
```

## What's Included

This package only re-exports two main components:
- `Workbook` - The main Excel workbook class
- `FileFormat` - Enum for Excel file formats (Version2016, Version2013, etc.)

## License

MIT License

## Note

This is a wrapper package. Spire.XLS Free edition has limitations (e.g., only first 3 worksheets). For full features, consider Spire.XLS commercial license.
