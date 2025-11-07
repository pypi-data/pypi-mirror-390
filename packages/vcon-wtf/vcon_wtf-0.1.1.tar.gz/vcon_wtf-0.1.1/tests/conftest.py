"""
Pytest configuration and shared fixtures.

This module contains shared fixtures and configuration for the test suite.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def sample_whisper_data() -> Dict[str, Any]:
    """Sample Whisper JSON data for testing."""
    return {
        "text": "Hello, this is a sample transcription from Whisper.",
        "language": "en",
        "duration": 5.2,
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.1,
                "text": "Hello, this is a sample transcription",
                "tokens": [50364, 15496, 11, 428, 318, 257, 6291, 11, 257, 1878, 13],
                "temperature": 0.0,
                "avg_logprob": -0.25,
                "compression_ratio": 2.1,
                "no_speech_prob": 0.01,
            },
            {
                "id": 1,
                "start": 2.1,
                "end": 5.2,
                "text": "from Whisper.",
                "tokens": [314, 1917, 13, 50257],
                "temperature": 0.0,
                "avg_logprob": -0.15,
                "compression_ratio": 1.8,
                "no_speech_prob": 0.005,
            },
        ],
    }


@pytest.fixture
def sample_deepgram_data() -> Dict[str, Any]:
    """Sample Deepgram JSON data for testing."""
    return {
        "metadata": {
            "transaction_key": "deprecated",
            "request_id": "test-request-id",
            "sha256": "test-sha256",
            "created": "2025-01-02T12:00:00.000Z",
            "duration": 5.2,
            "channels": 1,
            "model_info": {
                "name": "nova-2",
                "version": "2024-01-09",
                "uuid": "4d892fb6-7cc1-4e7a-a1b3-1c2e3f4a5b6c",
            },
        },
        "results": {
            "channels": [
                {
                    "alternatives": [
                        {
                            "transcript": "Hello, this is a sample transcription from Deepgram.",
                            "confidence": 0.94,
                            "words": [
                                {
                                    "word": "Hello",
                                    "start": 0.0,
                                    "end": 0.5,
                                    "confidence": 0.98,
                                    "speaker": 0,
                                    "speaker_confidence": 0.95,
                                    "punctuated_word": "Hello,",
                                },
                                {
                                    "word": "this",
                                    "start": 0.6,
                                    "end": 0.8,
                                    "confidence": 0.96,
                                    "speaker": 0,
                                    "speaker_confidence": 0.95,
                                    "punctuated_word": "this",
                                },
                            ],
                        }
                    ]
                }
            ]
        },
    }


@pytest.fixture
def sample_assemblyai_data() -> Dict[str, Any]:
    """Sample AssemblyAI JSON data for testing."""
    with open(Path(__file__).parent / "fixtures" / "assemblyai_sample.json", "r") as f:
        return json.load(f)


@pytest.fixture
def sample_wtf_document() -> Dict[str, Any]:
    """Sample WTF document for testing."""
    return {
        "transcript": {
            "text": "Hello, this is a sample transcription.",
            "language": "en-US",
            "duration": 5.2,
            "confidence": 0.95,
        },
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.1,
                "text": "Hello, this is a sample transcription",
                "confidence": 0.96,
                "speaker": 0,
            },
            {
                "id": 1,
                "start": 2.1,
                "end": 5.2,
                "text": "from the test.",
                "confidence": 0.94,
                "speaker": 0,
            },
        ],
        "metadata": {
            "created_at": "2025-01-02T12:00:00Z",
            "processed_at": "2025-01-02T12:00:15Z",
            "provider": "test",
            "model": "test-model",
            "processing_time": 15.2,
            "audio": {
                "duration": 5.2,
                "sample_rate": 16000,
                "channels": 1,
                "format": "wav",
            },
            "options": {},
        },
    }


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for test outputs."""
    return tmp_path / "output"
