# sampdfextractor/utils.py

import fitz  # PyMuPDF

def is_scanned_pdf(pdf_path: str) -> bool:
    """
    Detect if a PDF is scanned (image-based) or text-based.
    Returns True if scanned, False if normal.
    """
    doc = fitz.open(pdf_path)
    text_pages = 0

    for page in doc:
        text = page.get_text("text").strip()
        if text:
            text_pages += 1

    ratio = text_pages / len(doc)
    return ratio < 0.5  # If <50% pages have text, treat as scanned


def extract_text_from_pdf(pdf_path: str):
    """
    Extract text from each page of a normal (non-scanned) PDF.
    Returns a list of dicts: [{"page": n, "text": "..."}]
    """
    doc = fitz.open(pdf_path)
    data = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        data.append({"page": i + 1, "text": text})
    return data
