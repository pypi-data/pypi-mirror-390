"""Utilities for handling PDF documents."""
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader

PdfSource = str | Path | BinaryIO


def extract_text_from_pdf(pdf_source: PdfSource, *, skip_empty_lines: bool = True) -> str:
    """Extract all textual content from a PDF.

    Args:
        pdf_source: Path to a PDF file or a binary file-like object pointing to a PDF.
        skip_empty_lines: When ``True`` empty lines are removed from the output.

    Returns:
        The concatenated text content of the PDF.
    """

    if isinstance(pdf_source, str | Path):
        pdf_path = Path(pdf_source).expanduser().resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF filde not found: {pdf_path}")
        reader = PdfReader(str(pdf_path))
    else:
        binary_stream = pdf_source
        if binary_stream.seekable():
            binary_stream.seek(0)
        reader = PdfReader(binary_stream)

    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if skip_empty_lines:
            cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(cleaned_lines)
        page_texts.append(text.strip())

    return "\n\n".join(filter(None, page_texts))
