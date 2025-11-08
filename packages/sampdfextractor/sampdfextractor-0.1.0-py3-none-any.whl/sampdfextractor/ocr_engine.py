# sampdfextractor/ocr_engine.py

import os
import easyocr
import fitz  # PyMuPDF
from PIL import Image

reader = easyocr.Reader(['en'], gpu=False)


def pdf_to_images(pdf_path: str, output_folder: str = "images_temp"):
    """
    Convert each page of a PDF into an image (PNG format).
    Returns a list of image file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        img_path = os.path.join(output_folder, f"page_{i + 1}.png")
        pix.save(img_path)
        image_paths.append(img_path)

    return image_paths


def ocr_from_images(image_paths: list):
    """
    Run OCR (EasyOCR) on each image and extract text.
    Returns a list of dicts: [{"page": n, "text": "..."}]
    """
    all_pages = []
    for i, img_path in enumerate(image_paths):
        result = reader.readtext(img_path, detail=0)
        text = "\n".join(result)
        all_pages.append({"page": i + 1, "text": text})
    return all_pages
