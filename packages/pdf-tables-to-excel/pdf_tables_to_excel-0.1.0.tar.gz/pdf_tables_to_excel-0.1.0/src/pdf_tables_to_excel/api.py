from __future__ import annotations

from typing import List

from .docling_backend import extract_tables, TableData
from .excel_writer import build_sheet_specs, write_tables_to_excel


def convert_pdf_to_excel(
    input_pdf: str,
    output_xlsx: str,
    profile: str = "default",
    sheet_naming: str = "sequential",
    include_empty: bool = False,
) -> None:
    """
    High-level API: PDF -> nicely formatted Excel workbook.

    - input_pdf: path to PDF file
    - output_xlsx: path to Excel workbook to create
    - profile: formatting profile (currently only 'default')
    - sheet_naming: 'sequential' or 'by_page'
    - include_empty: if False, tables with 0 rows are skipped
    """
    tables: List[TableData] = extract_tables(input_pdf)

    if not include_empty:
        tables = [t for t in tables if not t.df.empty]

    sheet_specs = build_sheet_specs(tables, sheet_naming=sheet_naming)
    write_tables_to_excel(sheet_specs, output_xlsx, profile=profile)


__all__ = [
    "convert_pdf_to_excel",
    "extract_tables",
]
