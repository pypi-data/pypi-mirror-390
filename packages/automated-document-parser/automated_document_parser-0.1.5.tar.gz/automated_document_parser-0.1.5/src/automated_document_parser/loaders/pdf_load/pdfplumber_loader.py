"""
PDFPlumber loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/pdfplumber/
"""

import logging
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class PDFPlumberLoader(BasePDFLoader):
    """
    PDF loader using pdfplumber backend.

    Extracts text and table data from PDFs with high accuracy.
    No API key required - works locally.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using pdfplumber.

        Returns:
            List of LangChain Document objects

        Raises:
            ImportError: If langchain-community or pdfplumber is not installed
        """
        try:
            from langchain_community.document_loaders import (
                PDFPlumberLoader as LCPDFPlumberLoader,
            )

            loader = LCPDFPlumberLoader(str(self.file_path))
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import PDFPlumberLoader: {e}")
            raise ImportError(
                f"langchain-community and pdfplumber are required for PDFPlumber loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with PDFPlumber: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-community pdfplumber"
