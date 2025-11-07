"""
vCon WTF Library.

A Python library for converting transcript JSONs to/from the IETF World Transcription Format (WTF).
Supports major transcription providers including Whisper, Deepgram, AssemblyAI, and more.
"""

__version__ = "0.1.0"
__author__ = "vCon Development Team"
__email__ = "vcon@ietf.org"

from .core.converter import BaseConverter
from .core.models import WTFDocument, WTFSegment, WTFTranscript, WTFWord
from .core.validator import validate_wtf_document
from .exceptions import (
    AudioProcessingError,
    ConfigurationError,
    ConversionError,
    ProviderError,
    ValidationError,
)

__all__ = [
    "WTFDocument",
    "WTFTranscript",
    "WTFSegment",
    "WTFWord",
    "validate_wtf_document",
    "BaseConverter",
    "ConversionError",
    "ValidationError",
    "ProviderError",
    "ConfigurationError",
    "AudioProcessingError",
]
