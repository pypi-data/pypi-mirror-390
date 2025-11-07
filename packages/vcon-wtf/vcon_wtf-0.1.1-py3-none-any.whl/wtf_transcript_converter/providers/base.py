"""
Base provider converter implementation.

This module provides the base implementation for provider-specific converters.
"""

from abc import abstractmethod
from typing import Any, Dict

from ..core.converter import FromWTFConverter, ToWTFConverter
from ..core.models import WTFDocument


class BaseProviderConverter(ToWTFConverter, FromWTFConverter):
    """Base class for provider-specific converters."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    def convert_to_wtf(self, data: Dict[str, Any]) -> WTFDocument:
        """Convert provider-specific data to WTF format."""
        pass

    @abstractmethod
    def convert_from_wtf(self, wtf_doc: WTFDocument) -> Dict[str, Any]:
        """Convert WTF document to provider-specific format."""
        pass

    def convert(self, data: Any) -> Any:
        """Generic convert method - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement convert method")
