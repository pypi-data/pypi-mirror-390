
## 🧩 8️⃣ `setup.py`


from setuptools import setup, find_packages

setup(
    name="sampdfextractor",
    version="0.1.0",
    author="Samrendra Vishwakarma",
    author_email="samrendradev@gmail.com",
    description="Automatically detect and extract text from scanned and normal PDFs.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sam670/sampdfextractor",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF",
        "easyocr",
        "pandas",
        "Pillow",
    ],
    python_requires=">=3.8",
)
