"""
Pydantic data models for EDC.
"""

from deepcompress.models.document import Entity, ExtractedDocument, Page, Table
from deepcompress.models.response import CompressionResult, LLMResponse

__all__ = [
    "ExtractedDocument",
    "Page",
    "Entity",
    "Table",
    "CompressionResult",
    "LLMResponse",
]

