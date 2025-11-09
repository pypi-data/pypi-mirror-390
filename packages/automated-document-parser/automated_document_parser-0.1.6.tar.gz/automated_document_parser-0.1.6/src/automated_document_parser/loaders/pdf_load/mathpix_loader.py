"""
Mathpix API loader implementation.

Reference: https://python.langchain.com/docs/integrations/document_loaders/mathpix/
"""

import logging
import os
from typing import List

from langchain_core.documents import Document

from .base import BasePDFLoader

logger = logging.getLogger(__name__)


class MathpixPDFLoader(BasePDFLoader):
    """
    PDF loader using Mathpix API backend.

    Specialized for converting PDFs with mathematical formulas, tables, and diagrams.
    Requires MATHPIX_API_KEY environment variable or mathpix_api_key in kwargs.
    """

    def load(self) -> List[Document]:
        """
        Load PDF using Mathpix API.

        Returns:
            List of LangChain Document objects

        Raises:
            ValueError: If API key is not provided
            ImportError: If langchain-community is not installed
        """
        try:
            from langchain_community.document_loaders import (
                MathpixPDFLoader as LCMathpixPDFLoader,
            )

            # Check for API key
            api_key = self.kwargs.get("mathpix_api_key") or os.environ.get(
                "MATHPIX_API_KEY"
            )
            if not api_key:
                raise ValueError(
                    "MATHPIX_API_KEY not found. Set it as environment variable or pass as mathpix_api_key parameter."
                )

            # Set environment variable if passed as parameter
            if "mathpix_api_key" in self.kwargs:
                os.environ["MATHPIX_API_KEY"] = self.kwargs["mathpix_api_key"]

            loader = LCMathpixPDFLoader(str(self.file_path))
            return loader.load()

        except ImportError as e:
            logger.error(f"Failed to import MathpixPDFLoader: {e}")
            raise ImportError(
                f"langchain-community is required for Mathpix loader. {self.get_install_command()}"
            )
        except Exception as e:
            logger.error(f"Error loading PDF with Mathpix: {e}")
            raise

    @staticmethod
    def get_install_command() -> str:
        """
        Return the command to install required dependencies.

        Returns:
            Installation command string
        """
        return "pip install langchain-community"
