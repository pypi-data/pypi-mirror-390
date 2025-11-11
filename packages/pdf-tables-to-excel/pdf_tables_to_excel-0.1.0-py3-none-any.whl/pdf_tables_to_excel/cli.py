from __future__ import annotations

import argparse
import sys

from .api import convert_pdf_to_excel


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Extract tables from a PDF using Docling and export to a nicely formatted Excel workbook."
    )
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_xlsx", help="Path to the output Excel (.xlsx) file")

    parser.add_argument(
        "--profile",
        default="default",
        help="Formatting profile to use (default: 'default')",
    )
    parser.add_argument(
        "--sheet-naming",
        default="sequential",
        choices=["sequential", "by_page"],
        help="Strategy for naming sheets (default: 'sequential')",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Include tables with zero rows (default: skip them)",
    )

    args = parser.parse_args(argv)

    convert_pdf_to_excel(
        input_pdf=args.input_pdf,
        output_xlsx=args.output_xlsx,
        profile=args.profile,
        sheet_naming=args.sheet_naming,
        include_empty=args.include_empty,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
