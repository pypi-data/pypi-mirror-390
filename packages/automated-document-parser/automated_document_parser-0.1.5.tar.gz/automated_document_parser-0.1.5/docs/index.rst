Automated Document Parser Documentation
========================================

Welcome to the Automated Document Parser documentation!

**Automated Document Parser** is a powerful and intelligent document processing library built on top of LangChain. It provides automatic file type detection and loading for various document formats, making it easy to build RAG (Retrieval-Augmented Generation) applications.

Features
--------

* 🚀 **Automatic File Type Detection** - Intelligently detects and processes 10+ file formats
* 📄 **Multiple PDF Loaders** - 9 different PDF loading methods for various use cases
* 🔧 **Modular Architecture** - Clean separation with ``file_load/`` and ``pdf_load/`` modules
* 🎯 **Easy Integration** - Simple API that works seamlessly with LangChain
* 📊 **Structured Data Support** - Handle CSV, JSON, and other structured formats
* 🔌 **Extensible Design** - Easy to add custom loaders

Supported File Types
---------------------

**Text Files:**
  - ``.txt`` - Plain text files
  - ``.md`` - Markdown files

**Structured Data:**
  - ``.csv`` - CSV files with encoding support
  - ``.json`` - JSON files with jq schema filtering

**Documents:**
  - ``.docx`` - Microsoft Word documents
  - ``.html`` - HTML files

**PDF Files (9 methods):**
  - ``pypdf`` - Basic PDF text extraction (default)
  - ``unstructured`` - Advanced OCR and layout detection
  - ``amazon_textract`` - AWS Textract for high-accuracy OCR
  - ``mathpix`` - Specialized for mathematical formulas
  - ``pdfplumber`` - High accuracy text and table extraction
  - ``pypdfium2`` - Google PDFium library
  - ``pymupdf`` - PyMuPDF (fitz) backend
  - ``pymupdf4llm`` - LLM-optimized extraction
  - ``opendataloader`` - Advanced multi-format parsing

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install automated-document-parser

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from automated_document_parser import DocumentParser

   # Initialize the parser
   parser = DocumentParser()

   # Parse a single document (auto-detects file type)
   documents = parser.parse("path/to/document.pdf")

   # Parse multiple documents
   files = ["doc1.txt", "data.csv", "report.pdf"]
   results = parser.parse_multiple(files)

Advanced PDF Loading
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from automated_document_parser.loaders import PDFLoader

   # Use specific PDF loading method
   loader = PDFLoader("document.pdf", method="pdfplumber")
   documents = loader.load()

   # Use Mathpix for mathematical content
   loader = PDFLoader(
       "math_paper.pdf",
       method="mathpix",
       mathpix_app_id="your_id",
       mathpix_app_key="your_key"
   )
   documents = loader.load()

Direct Loader Usage
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from automated_document_parser.loaders.file_load import (
       TextFileLoader,
       CSVFileLoader,
       JSONFileLoader
   )

   # Load text file with specific encoding
   loader = TextFileLoader("file.txt", encoding="utf-8")
   docs = loader.load()

   # Load CSV file
   csv_loader = CSVFileLoader("data.csv")
   csv_docs = csv_loader.load()

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api
   modules

.. toctree::
   :maxdepth: 2
   :caption: Additional Resources

   GitHub Repository <https://github.com/Pulkit12dhingra/automated-document-parser>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
