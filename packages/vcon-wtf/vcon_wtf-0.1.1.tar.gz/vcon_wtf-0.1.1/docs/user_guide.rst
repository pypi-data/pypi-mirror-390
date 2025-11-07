User Guide
==========

This comprehensive guide covers all aspects of using the vCon WTF library.

Getting Started
---------------

Installation
~~~~~~~~~~~~

See the :doc:`installation` guide for detailed installation instructions.

Basic Concepts
~~~~~~~~~~~~~~

vCon WTF standardizes transcription data across multiple providers by converting them to and from the IETF World Transcription Format (WTF). This enables:

* **Interoperability**: Use transcriptions from any supported provider
* **Consistency**: Standardized format for all transcriptions
* **Validation**: Robust validation of transcription data
* **Cross-Provider Testing**: Compare results across providers

Core Components
~~~~~~~~~~~~~~~

* **WTFDocument**: The standardized transcription format
* **Provider Converters**: Convert between provider formats and WTF
* **Validator**: Validate WTF documents
* **CLI Tool**: Command-line interface for conversions

Working with WTF Documents
--------------------------

WTF Document Structure
~~~~~~~~~~~~~~~~~~~~~~

A WTF document contains:

.. code-block:: python

   {
     "transcript": {
       "text": "Hello, this is a test transcription.",
       "language": "en",
       "duration": 3.5,
       "confidence": 0.95
     },
     "segments": [
       {
         "start": 0.0,
         "end": 3.5,
         "text": "Hello, this is a test transcription.",
         "confidence": 0.95
       }
     ],
     "words": [
       {
         "word": "Hello,",
         "start": 0.0,
         "end": 0.5,
         "confidence": 0.99
       }
     ],
     "metadata": {
       "provider": "whisper",
       "model": "whisper-1",
       "created_at": "2024-01-01T00:00:00Z"
     }
   }

Creating WTF Documents
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.models import WTFDocument, WTFTranscript, WTFSegment, WTFWord

   # Create a WTF document manually
   transcript = WTFTranscript(
       text="Hello, world!",
       language="en",
       duration=2.0,
       confidence=0.95
   )

   segment = WTFSegment(
       start=0.0,
       end=2.0,
       text="Hello, world!",
       confidence=0.95
   )

   word = WTFWord(
       word="Hello,",
       start=0.0,
       end=0.5,
       confidence=0.99
   )

   wtf_doc = WTFDocument(
       transcript=transcript,
       segments=[segment],
       words=[word]
   )

Converting Between Formats
--------------------------

Provider to WTF
~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

WTF to Provider
~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import DeepgramConverter

   converter = DeepgramConverter()
   deepgram_data = converter.convert_from_wtf(wtf_doc)

Cross-Provider Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter, DeepgramConverter

   # Convert Whisper to WTF
   whisper_converter = WhisperConverter()
   wtf_doc = whisper_converter.convert_to_wtf(whisper_data)

   # Convert WTF to Deepgram
   deepgram_converter = DeepgramConverter()
   deepgram_data = deepgram_converter.convert_from_wtf(wtf_doc)

Validation
----------

Basic Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import validate_wtf_document

   is_valid, errors = validate_wtf_document(wtf_doc)

   if not is_valid:
       print("Validation errors:")
       for error in errors:
           print(f"  - {error}")

Advanced Validation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import WTFValidator

   validator = WTFValidator()

   # Add custom validation rules
   def confidence_check(doc):
       return doc.transcript.confidence > 0.5

   validator.add_custom_rule("confidence_check", confidence_check)

   is_valid, errors = validator.validate(wtf_doc)

Error Handling
--------------

Conversion Errors
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter
   from wtf_transcript_converter.exceptions import ConversionError

   converter = WhisperConverter()

   try:
       wtf_doc = converter.convert_to_wtf(invalid_data)
   except ConversionError as e:
       print(f"Conversion failed: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Validation Errors
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import validate_wtf_document
   from wtf_transcript_converter.exceptions import ValidationError

   try:
       is_valid, errors = validate_wtf_document(invalid_doc)
       if not is_valid:
           raise ValidationError(f"Validation failed: {errors}")
   except ValidationError as e:
       print(f"Validation error: {e}")

Command Line Interface
----------------------

Basic Commands
~~~~~~~~~~~~~~

Convert to WTF:

.. code-block:: bash

   vcon-wtf to-wtf input.json --provider whisper --output result.wtf.json

Convert from WTF:

.. code-block:: bash

   vcon-wtf from-wtf result.wtf.json --provider deepgram --output deepgram_output.json

Validate WTF document:

.. code-block:: bash

   vcon-wtf validate result.wtf.json

Cross-Provider Testing
~~~~~~~~~~~~~~~~~~~~~~

Test consistency:

.. code-block:: bash

   vcon-wtf cross-provider consistency input.json --verbose

Benchmark performance:

.. code-block:: bash

   vcon-wtf cross-provider performance input.json --iterations 5

Compare quality:

.. code-block:: bash

   vcon-wtf cross-provider quality input.json --output quality_report.json

Run all tests:

.. code-block:: bash

   vcon-wtf cross-provider all input.json --output-dir reports/

Advanced Usage
--------------

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from pathlib import Path
   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   input_dir = Path("input_files")
   output_dir = Path("output_files")

   for input_file in input_dir.glob("*.json"):
       with open(input_file, 'r') as f:
           data = json.load(f)

       wtf_doc = converter.convert_to_wtf(data)

       output_file = output_dir / f"{input_file.stem}.wtf.json"
       with open(output_file, 'w') as f:
           f.write(wtf_doc.model_dump_json(indent=2))

Custom Validation Rules
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import WTFValidator

   validator = WTFValidator()

   # Add custom rules
   validator.add_custom_rule(
       "min_confidence",
       lambda doc: doc.transcript.confidence >= 0.8
   )

   validator.add_custom_rule(
       "max_duration",
       lambda doc: doc.transcript.duration <= 3600  # 1 hour
   )

   is_valid, errors = validator.validate(wtf_doc)

Provider-Specific Features
--------------------------

Whisper Features
~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

   # Access Whisper-specific features
   for segment in wtf_doc.segments:
       print(f"Log probability: {segment.confidence}")

   for word in wtf_doc.words:
       print(f"Word probability: {word.confidence}")

Deepgram Features
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import DeepgramConverter

   converter = DeepgramConverter()
   wtf_doc = converter.convert_to_wtf(deepgram_data)

   # Access Deepgram-specific features
   print(f"Speaker count: {len(wtf_doc.speakers)}")
   print(f"Channel count: {len(deepgram_data['results']['channels'])}")

AssemblyAI Features
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import AssemblyAIConverter

   converter = AssemblyAIConverter()
   wtf_doc = converter.convert_to_wtf(assemblyai_data)

   # Access AssemblyAI-specific features
   print(f"Utterance count: {len(assemblyai_data['utterances'])}")
   print(f"Language code: {assemblyai_data['language_code']}")

Best Practices
--------------

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Cache Results**: Store converted WTF documents to avoid re-processing
2. **Batch Processing**: Process multiple files in batches
3. **Async Processing**: Use async/await for I/O operations
4. **Memory Management**: Process large files in chunks

.. code-block:: python

   import asyncio
   from wtf_transcript_converter.providers import WhisperConverter

   async def process_files_async(files):
       converter = WhisperConverter()
       tasks = []

       for file in files:
           task = asyncio.create_task(process_file_async(converter, file))
           tasks.append(task)

       results = await asyncio.gather(*tasks)
       return results

   async def process_file_async(converter, file):
       with open(file, 'r') as f:
           data = json.load(f)

       wtf_doc = converter.convert_to_wtf(data)
       return wtf_doc

Error Handling
~~~~~~~~~~~~~~

1. **Validate Input**: Always validate input data before conversion
2. **Handle Exceptions**: Implement proper exception handling
3. **Log Errors**: Log errors for debugging and monitoring
4. **Graceful Degradation**: Provide fallback options when possible

.. code-block:: python

   import logging
   from wtf_transcript_converter.providers import WhisperConverter
   from wtf_transcript_converter.exceptions import ConversionError

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   def safe_convert(converter, data):
       try:
           # Validate input
           if not data or 'text' not in data:
               raise ValueError("Invalid input data")

           # Convert
           wtf_doc = converter.convert_to_wtf(data)

           # Validate output
           is_valid, errors = validate_wtf_document(wtf_doc)
           if not is_valid:
               raise ValidationError(f"Output validation failed: {errors}")

           return wtf_doc

       except ConversionError as e:
           logger.error(f"Conversion failed: {e}")
           raise
       except Exception as e:
           logger.error(f"Unexpected error: {e}")
           raise

Data Quality
~~~~~~~~~~~~

1. **Check Confidence Scores**: Monitor confidence scores for quality
2. **Validate Timing**: Ensure timing information is accurate
3. **Cross-Validate**: Use multiple providers for important transcriptions
4. **Quality Metrics**: Track quality metrics over time

.. code-block:: python

   def analyze_quality(wtf_doc):
       metrics = {
           'overall_confidence': wtf_doc.transcript.confidence,
           'avg_word_confidence': sum(word.confidence for word in wtf_doc.words) / len(wtf_doc.words),
           'low_confidence_words': sum(1 for word in wtf_doc.words if word.confidence < 0.5),
           'duration': wtf_doc.transcript.duration,
           'word_count': len(wtf_doc.words)
       }

       return metrics

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**
^^^^^^^^^^^^^^^^^

If you encounter import errors:

.. code-block:: bash

   # Check Python version
   python --version  # Should be 3.10 or higher

   # Reinstall package
   pip uninstall vcon-wtf
   pip install vcon-wtf

**Validation Errors**
^^^^^^^^^^^^^^^^^^^^^

If validation fails:

.. code-block:: python

   # Check WTF document structure
   print(wtf_doc.model_dump_json(indent=2))

   # Validate step by step
   is_valid, errors = validate_wtf_document(wtf_doc)
   for error in errors:
       print(f"Error: {error}")

**Conversion Errors**
^^^^^^^^^^^^^^^^^^^^^

If conversion fails:

.. code-block:: python

   # Check input data format
   print(json.dumps(input_data, indent=2))

   # Try with minimal data
   minimal_data = {"text": "test", "language": "en", "duration": 1.0}
   wtf_doc = converter.convert_to_wtf(minimal_data)

**CLI Issues**
^^^^^^^^^^^^^^

If CLI commands fail:

.. code-block:: bash

   # Check installation
   pip show vcon-wtf

   # Test with verbose output
   vcon-wtf --help

   # Check file permissions
   ls -la input.json

Getting Help
------------

* **Documentation**: Check the full documentation
* **GitHub Issues**: Report bugs and request features
* **Discord Community**: Join our Discord for support
* **Email Support**: Contact us at vcon@ietf.org

Next Steps
----------

* :doc:`api_reference` - Complete API documentation
* :doc:`providers` - Provider-specific documentation
* :doc:`cross_provider_testing` - Cross-provider testing guide
* :doc:`examples` - More examples and use cases
