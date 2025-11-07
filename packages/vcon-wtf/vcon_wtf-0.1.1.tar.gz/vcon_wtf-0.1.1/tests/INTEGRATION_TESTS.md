# Integration Tests with Real Transcription Providers

This directory contains integration tests that can make actual API calls to transcription providers when API keys are provided.

## Setup

### 1. Install Integration Dependencies

```bash
uv sync --extra integration
```

### 2. Set API Keys

Set environment variables for the providers you want to test:

```bash
# For Whisper (OpenAI)
export OPENAI_API_KEY="your-openai-api-key"

# For Deepgram
export DEEPGRAM_API_KEY="your-deepgram-api-key"

# For AssemblyAI
export ASSEMBLYAI_API_KEY="your-assemblyai-api-key"
```

### 3. Test Audio File

A test audio file (`test_audio.wav`) is automatically created in `tests/fixtures/`. This is a 3-second 440Hz tone that can be used for testing.

For better results, you can replace it with a real audio file containing speech.

## Running Integration Tests

### Run All Integration Tests

```bash
# Run all integration tests (will skip if no API keys)
uv run pytest tests/test_integration.py -v

# Run real API integration tests
uv run pytest tests/test_real_api_integration.py -v
```

### Run Tests for Specific Providers

```bash
# Run only Whisper integration tests
uv run pytest tests/test_integration.py::TestWhisperIntegration -v

# Run only Deepgram integration tests
uv run pytest tests/test_integration.py::TestDeepgramIntegration -v

# Run only AssemblyAI integration tests
uv run pytest tests/test_integration.py::TestAssemblyAIIntegration -v
```

### Run with Specific API Keys

```bash
# Run with only Whisper API key
OPENAI_API_KEY="your-key" uv run pytest tests/test_real_api_integration.py::TestRealWhisperAPI -v

# Run with only Deepgram API key
DEEPGRAM_API_KEY="your-key" uv run pytest tests/test_real_api_integration.py::TestRealDeepgramAPI -v

# Run with only AssemblyAI API key
ASSEMBLYAI_API_KEY="your-key" uv run pytest tests/test_real_api_integration.py::TestRealAssemblyAIAPI -v
```

## Test Categories

### 1. Mock Integration Tests (`test_integration.py`)

These tests use mock responses that simulate real API responses. They test the conversion logic without making actual API calls.

- **TestWhisperIntegration**: Tests Whisper converter with mock data
- **TestDeepgramIntegration**: Tests Deepgram converter with mock data
- **TestAssemblyAIIntegration**: Tests AssemblyAI converter with mock data
- **TestCrossProviderIntegration**: Tests consistency across providers

### 2. Real API Integration Tests (`test_real_api_integration.py`)

These tests make actual API calls to the transcription providers. They require valid API keys and will transcribe real audio.

- **TestRealWhisperAPI**: Makes real calls to OpenAI Whisper API
- **TestRealDeepgramAPI**: Makes real calls to Deepgram API
- **TestRealAssemblyAIAPI**: Makes real calls to AssemblyAI API
- **TestCrossProviderComparison**: Compares results across providers

## Expected Behavior

### Without API Keys

Tests will be skipped with messages like:
```
SKIPPED - No API keys provided. Set OPENAI_API_KEY, DEEPGRAM_API_KEY, or ASSEMBLYAI_API_KEY to run integration tests.
```

### With API Keys

Tests will:
1. Make real API calls to transcription providers
2. Convert responses to WTF format
3. Validate the WTF documents
4. Test round-trip conversion
5. Print success messages with transcribed text

Example output:
```
✅ Whisper API test successful. Transcribed: 'Hello, this is a test transcription from Whisper API...'
✅ Deepgram API test successful. Transcribed: 'Hello, this is a test transcription from Deepgram API...'
✅ AssemblyAI API test successful. Transcribed: 'Hello, this is a test transcription from AssemblyAI API...'
```

## Cost Considerations

**Warning**: These tests make real API calls and may incur costs:

- **Whisper**: $0.006 per minute of audio
- **Deepgram**: $0.0043 per minute of audio
- **AssemblyAI**: $0.00065 per minute of audio

The test audio file is only 3 seconds long, so costs are minimal, but be aware when running tests frequently.

## Troubleshooting

### Common Issues

1. **"No test audio file available"**
   - Ensure `tests/fixtures/test_audio.wav` exists
   - The file is created automatically, but you can replace it with a real audio file

2. **API Key Errors**
   - Verify your API keys are valid and have sufficient credits
   - Check that environment variables are set correctly

3. **Import Errors**
   - Run `uv sync --extra integration` to install API client dependencies

4. **Rate Limiting**
   - Some providers have rate limits; tests may fail if you run them too frequently
   - Wait a few minutes between test runs if you encounter rate limit errors

### Debug Mode

Run tests with verbose output to see detailed information:

```bash
uv run pytest tests/test_real_api_integration.py -v -s
```

## Adding New Providers

To add integration tests for a new provider:

1. Add the provider's API client to `integration` dependencies in `pyproject.toml`
2. Create a new test class in `test_real_api_integration.py`
3. Implement the API call logic in the test methods
4. Add the provider's API key environment variable
5. Update this README with the new provider information
