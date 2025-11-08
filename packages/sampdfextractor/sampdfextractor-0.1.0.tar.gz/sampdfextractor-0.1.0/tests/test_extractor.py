# tests/test_extractor.py

from sampdfextractor import extract_pdf
import os

def test_extraction():
    sample_pdf = "samples/sample.pdf"  # put a small test PDF here
    output = "test_output.json"
    data = extract_pdf(sample_pdf, output)
    assert isinstance(data, list)
    assert all("text" in p for p in data)
    assert os.path.exists(output)
