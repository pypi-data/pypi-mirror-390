"""
OpenDataLoader PDF loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/opendataloader/
"""

import logging
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class OpenDataLoaderPDFLoader(BasePDFLoader):
    """
    PDF loader using OpenDataLoader backend.

    Advanced PDF parsing with support for multiple formats and configurations.
    No API key required - works locally.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using OpenDataLoader.

        Returns:
            List of LangChain Document objects

        Raises:
            ImportError: If langchain-opendataloader-pdf is not installed
        """
        try:
            from langchain_opendataloader_pdf import (
                OpenDataLoaderPDFLoader as LCOpenDataLoaderPDFLoader,
            )

            # Get format from kwargs, default to "text"
            format_type = self.kwargs.get("format", "text")

            loader = LCOpenDataLoaderPDFLoader(
                file_path=str(self.file_path), format=format_type
            )
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import OpenDataLoaderPDFLoader: {e}")
            raise ImportError(
                f"langchain-opendataloader-pdf is required for OpenDataLoader loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with OpenDataLoader: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-opendataloader-pdf"
