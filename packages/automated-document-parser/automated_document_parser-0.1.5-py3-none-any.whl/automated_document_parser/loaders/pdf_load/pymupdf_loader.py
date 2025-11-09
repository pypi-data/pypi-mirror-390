"""
PyMuPDF loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/pymupdf/
"""

import logging
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class PyMuPDFLoader(BasePDFLoader):
    """
    PDF loader using PyMuPDF (fitz) backend.

    Fast PDF parsing with support for text, images, and metadata extraction.
    No API key required - works locally.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using PyMuPDF.

        Returns:
            List of LangChain Document objects

        Raises:
            ImportError: If langchain-community or pymupdf is not installed
        """
        try:
            from langchain_community.document_loaders import (
                PyMuPDFLoader as LCPyMuPDFLoader,
            )

            loader = LCPyMuPDFLoader(str(self.file_path))
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import PyMuPDFLoader: {e}")
            raise ImportError(
                f"langchain-community and pymupdf are required for PyMuPDF loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with PyMuPDF: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-community pymupdf"
