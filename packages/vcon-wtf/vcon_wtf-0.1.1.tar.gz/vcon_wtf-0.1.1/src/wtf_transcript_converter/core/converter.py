"""
Base converter framework for WTF transcript conversion.

This module provides abstract base classes for converting between
different transcript formats and WTF.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar

from .models import WTFDocument

T = TypeVar("T")


class BaseConverter(ABC):
    """Abstract base class for all converters."""

    @abstractmethod
    def convert(self, data: Any) -> Any:
        """Convert data from one format to another."""
        pass


class ToWTFConverter(BaseConverter):
    """Abstract base class for converters that convert TO WTF format."""

    @abstractmethod
    def convert(self, data: Dict[str, Any]) -> WTFDocument:
        """Convert provider-specific data to WTF format."""
        pass


class FromWTFConverter(BaseConverter):
    """Abstract base class for converters that convert FROM WTF format."""

    @abstractmethod
    def convert(self, wtf_doc: WTFDocument) -> Dict[str, Any]:
        """Convert WTF document to provider-specific format."""
        pass
