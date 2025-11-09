"""
PDF loader submodule with support for multiple backends.

Provides flexible PDF loading with built-in support for:
- PyPDF: Fast, simple PDF parsing (default)
- Unstructured: Advanced parsing with API support
- Amazon Textract: OCR for scanned documents
- Mathpix: Specialized for mathematical formulas and diagrams
- PDFPlumber: High accuracy text and table extraction
- PyPDFium2: Fast parsing using Google's PDFium library
- PyMuPDF: Fast parsing with text, images, and metadata extraction
- PyMuPDF4LLM: Optimized for LLM processing
- OpenDataLoader: Advanced parsing with multiple format support

Users can also provide custom loader classes for additional flexibility.
"""

from .base import BasePDFLoader, PDFLoaderMethod
from .loader import PDFLoader, load_pdf
from .pypdf_loader import PyPDFLoaderImpl
from .textract_loader import AmazonTextractPDFLoader
from .unstructured_loader import UnstructuredPDFLoader
from .mathpix_loader import MathpixPDFLoader
from .pdfplumber_loader import PDFPlumberLoader
from .pypdfium2_loader import PyPDFium2Loader
from .pymupdf_loader import PyMuPDFLoader
from .pymupdf4llm_loader import PyMuPDF4LLMLoader
from .opendataloader_loader import OpenDataLoaderPDFLoader

__all__ = [
    # Main API
    "PDFLoader",
    "load_pdf",
    # Base classes and types
    "BasePDFLoader",
    "PDFLoaderMethod",
    # Individual loader implementations (for advanced usage)
    "PyPDFLoaderImpl",
    "UnstructuredPDFLoader",
    "AmazonTextractPDFLoader",
    "MathpixPDFLoader",
    "PDFPlumberLoader",
    "PyPDFium2Loader",
    "PyMuPDFLoader",
    "PyMuPDF4LLMLoader",
    "OpenDataLoaderPDFLoader",
]
