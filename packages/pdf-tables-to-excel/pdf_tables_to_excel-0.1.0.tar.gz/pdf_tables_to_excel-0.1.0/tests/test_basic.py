import pandas as pd
from pathlib import Path

from pdf_tables_to_excel.docling_backend import TableMeta, TableData
from pdf_tables_to_excel.excel_writer import build_sheet_specs, write_tables_to_excel


def test_write_simple_table(tmp_path: Path):
    # Create a small fake table
    df = pd.DataFrame(
        {
            "Metric": ["Net revenues", "Operating income"],
            "1Q 2025": ["1,234", "567"],
            "% Change": ["21.8%", "(4.3%)"],
        }
    )

    # Minimal metadata (normally comes from Docling)
    meta = TableMeta(
        global_index=0,
        page_number=1,
        table_index_on_page=0,
        caption="Test Summary Table",
        source_pdf="dummy.pdf",
    )
    table = TableData(df=df, meta=meta)

    # Build sheet specs and write Excel
    sheet_specs = build_sheet_specs([table], sheet_naming="sequential")
    out_file = tmp_path / "test_output.xlsx"
    write_tables_to_excel(sheet_specs, str(out_file), profile="default")

    # Assert: file exists and is non-empty
    assert out_file.exists()
    assert out_file.stat().st_size > 0
