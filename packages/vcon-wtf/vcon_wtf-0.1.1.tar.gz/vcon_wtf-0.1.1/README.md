# vCon WTF

A Python library for converting transcript JSONs to/from the IETF World Transcription Format (WTF). This library provides seamless conversion between different transcription provider formats and the standardized WTF format, with full integration support for vCon containers.

## Features

- **Multi-Provider Support**: Convert transcripts from Whisper, Deepgram, AssemblyAI, Rev.ai, Canary (NVIDIA), Parakeet (NVIDIA), Google Cloud Speech-to-Text, Amazon Transcribe, Azure Speech Services, and more
- **WTF Compliance**: Full adherence to the IETF World Transcription Format specification
- **vCon Integration**: Seamless integration with vcon-lib for vCon container operations
- **Command-Line Interface**: Easy-to-use CLI for batch conversion and validation
- **Comprehensive Validation**: Robust validation of WTF documents and input formats
- **Quality Metrics**: Built-in quality assessment and confidence score normalization

## Installation

```bash
# Install from PyPI (when available)
pip install vcon-wtf

# Or install from source
git clone https://github.com/vcon-dev/wtf-transcript-converter.git
cd wtf-transcript-converter
uv sync
```

## Quick Start

### Basic Usage

```python
from wtf_transcript_converter import WTFDocument, validate_wtf_document
from wtf_transcript_converter.providers import WhisperConverter

# Convert Whisper output to WTF
whisper_data = {...}  # Your Whisper JSON data
converter = WhisperConverter()
wtf_doc = converter.convert(whisper_data)

# Validate the WTF document
is_valid, errors = validate_wtf_document(wtf_doc)
if is_valid:
    print("WTF document is valid!")
else:
    print(f"Validation errors: {errors}")
```

### Command-Line Usage

```bash
# Convert to WTF format
vcon-wtf to-wtf input.json --provider whisper --output output.json

# Convert from WTF format
vcon-wtf from-wtf input.json --provider deepgram --output output.json

# Validate WTF document
vcon-wtf validate input.json

# Batch conversion
vcon-wtf batch --input-dir ./transcripts --output-dir ./wtf --provider auto
```

### vCon Integration

```python
from vcon import Vcon
from wtf_transcript_converter import VConWTFAttachment

# Create vCon container with WTF transcription
vcon = Vcon()
wtf_attachment = VConWTFAttachment.create_from_wtf(wtf_doc)
vcon = wtf_attachment.add_to_vcon(vcon)
```

## Supported Providers

- **Whisper**: OpenAI's speech recognition system
- **Deepgram**: Real-time speech-to-text API
- **AssemblyAI**: AI-powered transcription service
- **Rev.ai**: Professional transcription service
- **Canary**: NVIDIA's advanced speech recognition model (via Hugging Face)
- **Parakeet**: NVIDIA's efficient transducer-based model (via Hugging Face)
- **Google Cloud Speech-to-Text**: Google's speech recognition service (planned)
- **Amazon Transcribe**: AWS speech-to-text service (planned)
- **Azure Speech Services**: Microsoft's speech recognition platform (planned)
- **Speechmatics**: Real-time and batch speech recognition (planned)

## Hugging Face Integration

The library includes support for NVIDIA's Canary and Parakeet models via Hugging Face:

### Setup for Hugging Face Models

```bash
# Install with Hugging Face dependencies
uv add --group integration transformers torch librosa soundfile

# Set your Hugging Face token (optional, for gated models)
export HF_TOKEN=your_huggingface_token_here
```

### Using Canary and Parakeet

```python
from wtf_transcript_converter.providers import CanaryConverter, ParakeetConverter

# Canary converter
canary_converter = CanaryConverter()
canary_result = canary_converter.transcribe_audio("audio.wav", language="en")
wtf_doc = canary_converter.convert_to_wtf(canary_result)

# Parakeet converter
parakeet_converter = ParakeetConverter()
parakeet_result = parakeet_converter.transcribe_audio("audio.wav", language="en")
wtf_doc = parakeet_converter.convert_to_wtf(parakeet_result)
```

### Command Line Usage

```bash
# Convert with Canary
vcon-wtf to-wtf canary_output.json --provider canary --output result.wtf.json

# Convert with Parakeet
vcon-wtf to-wtf parakeet_output.json --provider parakeet --output result.wtf.json
```

## Cross-Provider Testing

The library includes comprehensive cross-provider testing capabilities:

### Consistency Testing

```bash
# Test consistency across all providers
vcon-wtf cross-provider consistency input.json --verbose

# Generate detailed consistency report
vcon-wtf cross-provider consistency input.json --output consistency_report.json
```

### Performance Benchmarking

```bash
# Benchmark performance across providers
vcon-wtf cross-provider performance input.json --iterations 5

# Compare conversion speed and resource usage
vcon-wtf cross-provider performance input.json --output performance_report.json
```

### Quality Comparison

```bash
# Compare quality metrics across providers
vcon-wtf cross-provider quality input.json --verbose

# Generate quality analysis report
vcon-wtf cross-provider quality input.json --output quality_report.json
```

### Comprehensive Testing

```bash
# Run all cross-provider tests
vcon-wtf cross-provider all input.json --output-dir reports/

# This generates:
# - reports/consistency_report.json
# - reports/performance_report.json
# - reports/quality_report.json
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/vcon-dev/wtf-transcript-converter.git
cd wtf-transcript-converter
uv sync --dev
uv run pre-commit install
```

### Running Tests

```bash
uv run pytest
uv run pytest --cov=src/wtf_transcript_converter --cov-report=html
```

### Code Quality

```bash
uv run black src tests
uv run isort src tests
uv run flake8 src tests
uv run mypy src
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- **Repository**: https://github.com/vcon-dev/wtf-transcript-converter
- **Documentation**: https://vcon-wtf.readthedocs.io
- **vCon Specification**: https://github.com/vcon-dev/draft-ietf-vcon-core
- **WTF Extension Draft**: https://github.com/vcon-dev/draft-howe-vcon-wtf-extension

## Acknowledgments

- vCon Working Group for the WTF specification
- Transcription provider communities for format insights
- IETF for standardization framework
