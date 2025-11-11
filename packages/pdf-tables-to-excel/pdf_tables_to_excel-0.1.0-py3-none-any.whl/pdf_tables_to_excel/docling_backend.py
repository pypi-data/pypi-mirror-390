from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
from docling.document_converter import DocumentConverter


@dataclass
class TableMeta:
    """Metadata about a detected table."""
    global_index: int             # 0-based index across all tables
    page_number: Optional[int]    # 1-based page number, if available
    table_index_on_page: int      # 0-based index on that page
    caption: Optional[str] = None
    source_pdf: Optional[str] = None


@dataclass
class TableData:
    """A table as a DataFrame plus its metadata."""
    df: pd.DataFrame
    meta: TableMeta


def extract_tables(pdf_path: str) -> List[TableData]:
    """
    Use Docling to extract all tables from a PDF.

    Returns a list of TableData objects with DataFrames + metadata.
    """
    converter = DocumentConverter()
    conv_res = converter.convert(pdf_path)
    doc = conv_res.document

    tables: List[TableData] = []
    global_idx = 0

    page_table_counts = {}  # page_number -> count so far

    for table in getattr(doc, "tables", []):
        # Try to get page number if present; otherwise None
        page_number = getattr(table, "page_no", None)
        if page_number is None:
            page_number = getattr(table, "page_number", None)

        # Track index of table on its page
        if page_number is not None:
            page_table_counts.setdefault(page_number, 0)
            table_index_on_page = page_table_counts[page_number]
            page_table_counts[page_number] += 1
        else:
            table_index_on_page = 0

        caption = getattr(table, "caption", None)

        # Pass doc argument to avoid deprecation
        df = table.export_to_dataframe(doc=doc)

        meta = TableMeta(
            global_index=global_idx,
            page_number=page_number,
            table_index_on_page=table_index_on_page,
            caption=caption,
            source_pdf=pdf_path,
        )
        tables.append(TableData(df=df, meta=meta))
        global_idx += 1

    return tables
