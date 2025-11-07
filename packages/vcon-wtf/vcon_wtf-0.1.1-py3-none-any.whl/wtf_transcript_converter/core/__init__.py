"""
Core WTF functionality.

This module contains the core models, validation, and conversion logic
for the World Transcription Format (WTF).
"""

from .converter import BaseConverter, FromWTFConverter, ToWTFConverter
from .models import (
    VConWTFAttachment,
    WTFAudio,
    WTFDocument,
    WTFExtensions,
    WTFMetadata,
    WTFQuality,
    WTFSegment,
    WTFSpeaker,
    WTFTranscript,
    WTFWord,
)
from .validator import validate_wtf_document

__all__ = [
    "WTFDocument",
    "WTFTranscript",
    "WTFSegment",
    "WTFWord",
    "WTFSpeaker",
    "WTFMetadata",
    "WTFQuality",
    "WTFAudio",
    "WTFExtensions",
    "VConWTFAttachment",
    "validate_wtf_document",
    "BaseConverter",
    "ToWTFConverter",
    "FromWTFConverter",
]
