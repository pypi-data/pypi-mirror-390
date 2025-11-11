from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional
import re
import math

import numpy as np
import pandas as pd

from .docling_backend import TableData


class SheetNaming(str, Enum):
    SEQUENTIAL = "sequential"
    BY_PAGE = "by_page"


@dataclass
class SheetSpec:
    """One Excel sheet, possibly containing one or more tables."""
    name: str
    tables: List[TableData]


def _normalize_sheet_naming(value: str) -> SheetNaming:
    try:
        return SheetNaming(value)
    except ValueError:
        # Fallback to sequential if unknown
        return SheetNaming.SEQUENTIAL


def sanitize_sheet_title(text: str) -> str:
    """
    Turn an arbitrary caption into a safe, short Excel sheet title.
    """
    if not text:
        return "Table"

    # Remove characters Excel doesn't like: []:*?/\
    name = re.sub(r"[\[\]\:\*\?\/\\]", " ", str(text))
    # Collapse whitespace -> _
    name = re.sub(r"\s+", "_", name).strip("_")

    if not name:
        return "Table"

    # Excel limit is 31 chars
    return name[:31]


def make_sheet_name(table: TableData, naming: SheetNaming) -> str:
    meta = table.meta

    # Prefer caption if available
    base = None
    if meta.caption:
        base = sanitize_sheet_title(meta.caption)

    if naming == SheetNaming.SEQUENTIAL:
        if base:
            # Keep it unique by adding index suffix (if room)
            suffix = f"_{meta.global_index + 1}"
            if len(base) + len(suffix) <= 31:
                return base + suffix
            return base  # already truncated
        return f"Table_{meta.global_index + 1}"

    if naming == SheetNaming.BY_PAGE:
        page_str = meta.page_number or 0
        if base:
            candidate = f"{base}_P{page_str}"
            if len(candidate) <= 31:
                return candidate
            return base
        page_part = f"Page_{page_str}"
        return f"{page_part}_Table_{meta.table_index_on_page + 1}"

    # Fallback
    return f"Table_{meta.global_index + 1}"


def build_sheet_specs(
    tables: List[TableData],
    sheet_naming: str = "sequential",
) -> List[SheetSpec]:
    """
    For v0.1: each table gets its own sheet.
    """
    naming_enum = _normalize_sheet_naming(sheet_naming)
    specs: List[SheetSpec] = []

    for table in tables:
        name = make_sheet_name(table, naming_enum)
        specs.append(SheetSpec(name=name, tables=[table]))

    return specs


def _parse_text_number(value: str) -> Tuple[Optional[float], bool, bool]:
    """
    Try to parse a single cell string into a float, handling:
      - thousands separators
      - leading '$'
      - '%' (returned as fraction, i.e. 21.8% -> 0.218)
      - parentheses for negatives, e.g. '(4.3%)', '(2,345)'
    Returns: (numeric_value or None, had_percent, had_dollar)
    """
    if value is None:
        return None, False, False

    s = str(value).strip()
    if s == "" or s in {"-", "–", "—", "N/A", "n/a"}:
        return None, False, False

    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1].strip()

    has_percent = "%" in s
    has_dollar = "$" in s

    # Remove symbols, keep digits, dot, minus
    s = s.replace(",", "")
    s = s.replace("$", "")
    s = s.replace("%", "")

    if s == "":
        return None, has_percent, has_dollar

    try:
        val = float(s)
    except ValueError:
        return None, has_percent, has_dollar

    if neg:
        val = -val
    if has_percent:
        val = val / 100.0

    return val, has_percent, has_dollar


def infer_numeric_series(col: pd.Series) -> Tuple[pd.Series, Optional[str]]:
    """
    Try to interpret a text column as numeric (plain, %, or currency).

    Returns:
      - new_series: either original col or numeric col
      - excel_num_format: string or None

    If we fail or it's clearly not numeric, returns (original, None).
    """
    if col.empty:
        return col, None

    tmp = col.astype(str).str.strip()
    mask = ~tmp.isin(["", "-", "–", "—", "N/A", "n/a"])
    if mask.sum() == 0:
        return col, None

    vals: List[float] = []
    had_percent = 0
    had_dollar = 0
    parsed_count = 0

    # Parse only the mask-True values (strings we care about)
    for s in tmp[mask]:
        val, is_percent, is_dollar = _parse_text_number(s)
        if val is None:
            vals.append(np.nan)
        else:
            vals.append(float(val))
            parsed_count += 1
            if is_percent:
                had_percent += 1
            if is_dollar:
                had_dollar += 1

    total = mask.sum()
    if parsed_count == 0 or parsed_count / total < 0.6:
        # too few usable numeric values; leave column as-is
        return col, None

    # Build numeric series with float64 dtype and NaN for missing
    numeric = pd.Series(np.nan, index=col.index, dtype="float64")
    numeric.loc[mask] = vals  # vals contains floats or np.nan only

    # Decide Excel format
    if had_percent > 0 and had_dollar == 0:
        excel_fmt = "0.0%;(0.0%)"
    elif had_dollar > 0:
        excel_fmt = "$#,##0.0;($#,##0.0)"
    else:
        excel_fmt = "#,##0.0;(#,##0.0)"

    return numeric, excel_fmt


def write_tables_to_excel(
    sheet_specs: List[SheetSpec],
    output_path: str,
    profile: str = "default",
) -> None:
    """
    Write the given sheet specs to an Excel workbook with basic nice formatting.

    - Borders are applied ONLY to the actual table region (header + data rows).
    - We try to detect numeric / percent / currency columns and format them.
    """
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book

        header_fmt = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "border": 1,
            }
        )
        cell_fmt = workbook.add_format({"border": 1})
        default_number_fmt = workbook.add_format({"border": 1, "num_format": "#,##0.00"})
        default_int_fmt = workbook.add_format({"border": 1, "num_format": "#,##0"})

        for spec in sheet_specs:
            table = spec.tables[0]
            df = table.df.copy()

            sheet_name = spec.name[:31] if spec.name else "Table"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            sheet = writer.sheets[sheet_name]

            nrows, ncols = df.shape
            if ncols == 0:
                continue

            # Re-apply header row with our header format
            for col_idx, col_name in enumerate(df.columns):
                sheet.write(0, col_idx, col_name, header_fmt)

            for col_idx, col_name in enumerate(df.columns):
                col_series = df.iloc[:, col_idx]

                excel_num_format = None
                if pd.api.types.is_object_dtype(col_series):
                    numeric_series, excel_num_format = infer_numeric_series(col_series)
                    if excel_num_format is not None:
                        df.iloc[:, col_idx] = numeric_series
                        col_series = numeric_series

                col_format = cell_fmt
                if excel_num_format is not None:
                    col_format = workbook.add_format(
                        {"border": 1, "num_format": excel_num_format}
                    )
                elif pd.api.types.is_integer_dtype(col_series):
                    col_format = default_int_fmt
                elif pd.api.types.is_float_dtype(col_series):
                    col_format = default_number_fmt

                max_len_data = 0
                if not col_series.empty:
                    try:
                        length_series = col_series.astype(str).str.len()
                        max_len_data = length_series.max()
                        if isinstance(max_len_data, (pd.Series, pd.DataFrame)):
                            max_len_data = max_len_data.max()
                        if pd.isna(max_len_data):
                            max_len_data = 0
                        else:
                            max_len_data = int(float(max_len_data))
                    except Exception:
                        max_len_data = 0

                header_len = len(str(col_name))
                max_len = max(header_len, max_len_data)
                width = min(max_len + 2, 50)

                sheet.set_column(col_idx, col_idx, width)

                # Write cell-by-cell, cleaning NaN/NA/Inf to None
                for row_idx in range(nrows):
                    value = df.iloc[row_idx, col_idx]
                    if value is None or pd.isna(value) or (
                        isinstance(value, float)
                        and (math.isnan(value) or math.isinf(value))
                    ):
                        value = None
                    sheet.write(row_idx + 1, col_idx, value, col_format)

            sheet.freeze_panes(1, 0)
