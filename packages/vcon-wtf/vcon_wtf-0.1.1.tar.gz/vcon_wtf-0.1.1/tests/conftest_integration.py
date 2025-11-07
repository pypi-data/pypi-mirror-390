"""
Configuration for integration tests with real API providers.
"""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure pytest for integration tests."""
    # Add integration test markers
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line("markers", "whisper_api: marks tests that require Whisper API key")
    config.addinivalue_line("markers", "deepgram_api: marks tests that require Deepgram API key")
    config.addinivalue_line(
        "markers", "assemblyai_api: marks tests that require AssemblyAI API key"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip integration tests if no API keys."""
    skip_integration = True

    # Check if any API keys are provided
    if any(
        [
            os.getenv("OPENAI_API_KEY"),
            os.getenv("DEEPGRAM_API_KEY"),
            os.getenv("ASSEMBLYAI_API_KEY"),
        ]
    ):
        skip_integration = False

    if skip_integration:
        skip_marker = pytest.mark.skip(reason="No API keys provided for integration tests")
        for item in items:
            if "integration" in item.keywords or "real_api" in item.keywords:
                item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def api_keys_available():
    """Check if API keys are available for integration tests."""
    return {
        "whisper": bool(os.getenv("OPENAI_API_KEY")),
        "deepgram": bool(os.getenv("DEEPGRAM_API_KEY")),
        "assemblyai": bool(os.getenv("ASSEMBLYAI_API_KEY")),
    }


@pytest.fixture(scope="session")
def test_audio_file():
    """Get or create a test audio file for integration tests."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    audio_file = fixtures_dir / "test_audio.wav"

    if not audio_file.exists():
        # Create a simple test audio file
        # This would be a minimal WAV file for testing
        pytest.skip("No test audio file available. Place a test_audio.wav file in tests/fixtures/")

    return str(audio_file)
