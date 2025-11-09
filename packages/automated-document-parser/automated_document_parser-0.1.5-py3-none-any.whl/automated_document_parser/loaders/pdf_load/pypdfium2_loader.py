"""
PyPDFium2 loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/pypdfium2/
"""

import logging
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class PyPDFium2Loader(BasePDFLoader):
    """
    PDF loader using pypdfium2 backend.

    Fast and accurate PDF parsing using Google's PDFium library.
    No API key required - works locally.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using pypdfium2.

        Returns:
            List of LangChain Document objects

        Raises:
            ImportError: If langchain-community or pypdfium2 is not installed
        """
        try:
            from langchain_community.document_loaders import (
                PyPDFium2Loader as LCPyPDFium2Loader,
            )

            loader = LCPyPDFium2Loader(str(self.file_path))
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import PyPDFium2Loader: {e}")
            raise ImportError(
                f"langchain-community and pypdfium2 are required for PyPDFium2 loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with PyPDFium2: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-community pypdfium2"
