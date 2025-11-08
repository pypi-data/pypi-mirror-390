"""
Excel Processor

Example:
    >>> from excel_processor import Workbook, FileFormat
    >>> workbook = Workbook()
    >>> workbook.LoadFromFile("data.xlsx")
    >>> workbook.SaveToFile("output.xlsx", FileFormat.Version2016)
"""

from spire.xls import Workbook, FileFormat

__version__ = "0.1.0"
__all__ = [
    "Workbook",
    "FileFormat",
]
