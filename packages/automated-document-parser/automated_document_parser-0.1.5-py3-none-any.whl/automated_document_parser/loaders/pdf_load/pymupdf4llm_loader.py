"""
PyMuPDF4LLM loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/pymupdf4llm/
"""

import logging
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class PyMuPDF4LLMLoader(BasePDFLoader):
    """
    PDF loader using PyMuPDF4LLM backend.

    Optimized for LLM processing with enhanced text extraction and formatting.
    No API key required - works locally.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using PyMuPDF4LLM.

        Returns:
            List of LangChain Document objects

        Raises:
            ImportError: If langchain-pymupdf4llm is not installed
        """
        try:
            from langchain_pymupdf4llm import PyMuPDF4LLMLoader as LCPyMuPDF4LLMLoader

            loader = LCPyMuPDF4LLMLoader(str(self.file_path))
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import PyMuPDF4LLMLoader: {e}")
            raise ImportError(
                f"langchain-pymupdf4llm is required for PyMuPDF4LLM loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with PyMuPDF4LLM: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-pymupdf4llm"
