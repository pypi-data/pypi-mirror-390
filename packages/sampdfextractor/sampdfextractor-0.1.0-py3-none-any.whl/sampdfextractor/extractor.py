# sampdfextractor/extractor.py

import json
from .utils import is_scanned_pdf, extract_text_from_pdf
from .ocr_engine import pdf_to_images, ocr_from_images


def extract_pdf(pdf_path: str, output_json: str = "output.json"):
    """
    Automatically detect if the PDF is scanned or normal.
    Extract text accordingly and save output as JSON.
    """
    print(f"🔍 Checking PDF type: {pdf_path}")
    scanned = is_scanned_pdf(pdf_path)
    print("🖼️ Detected:", "Scanned PDF" if scanned else "Normal PDF")

    if scanned:
        image_paths = pdf_to_images(pdf_path)
        data = ocr_from_images(image_paths)
    else:
        data = extract_text_from_pdf(pdf_path)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Extraction complete. Data saved to {output_json}")
    return data
