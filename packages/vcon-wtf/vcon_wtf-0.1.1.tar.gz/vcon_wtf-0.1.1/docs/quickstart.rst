Quick Start Guide
=================

This guide will get you up and running with vCon WTF in just a few minutes.

Installation
------------

First, install the library:

.. code-block:: bash

   pip install vcon-wtf

Basic Usage
-----------

Python API
~~~~~~~~~~

Convert a Whisper transcription to WTF format:

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter
   from wtf_transcript_converter.core.models import WTFDocument

   # Sample Whisper data
   whisper_data = {
       "text": "Hello, this is a test transcription.",
       "language": "en",
       "duration": 3.5,
       "segments": [
           {
               "id": 0,
               "start": 0.0,
               "end": 3.5,
               "text": "Hello, this is a test transcription.",
               "avg_logprob": -0.4,
               "words": [
                   {"word": "Hello,", "start": 0.0, "end": 0.5, "probability": 0.99},
                   {"word": "this", "start": 0.6, "end": 0.8, "probability": 0.98},
                   {"word": "is", "start": 0.9, "end": 1.0, "probability": 0.99},
                   {"word": "a", "start": 1.1, "end": 1.2, "probability": 0.97},
                   {"word": "test", "start": 1.3, "end": 1.7, "probability": 0.96},
                   {"word": "transcription.", "start": 1.8, "end": 3.5, "probability": 0.95}
               ]
           }
       ]
   }

   # Convert to WTF format
   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

   # Access the standardized data
   print(f"Text: {wtf_doc.transcript.text}")
   print(f"Language: {wtf_doc.transcript.language}")
   print(f"Duration: {wtf_doc.transcript.duration}s")
   print(f"Confidence: {wtf_doc.transcript.confidence}")
   print(f"Segments: {len(wtf_doc.segments)}")

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

Convert using the CLI:

.. code-block:: bash

   # Convert to WTF format
   vcon-wtf to-wtf input.json --provider whisper --output result.wtf.json

   # Convert from WTF format
   vcon-wtf from-wtf result.wtf.json --provider deepgram --output deepgram_output.json

   # Validate WTF document
   vcon-wtf validate result.wtf.json

Cross-Provider Testing
~~~~~~~~~~~~~~~~~~~~~~

Test consistency across multiple providers:

.. code-block:: bash

   # Test consistency
   vcon-wtf cross-provider consistency input.json --verbose

   # Benchmark performance
   vcon-wtf cross-provider performance input.json --iterations 5

   # Compare quality
   vcon-wtf cross-provider quality input.json --output quality_report.json

   # Run all tests
   vcon-wtf cross-provider all input.json --output-dir reports/

Working with Different Providers
--------------------------------

Whisper
~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

   # Convert back to Whisper format
   whisper_output = converter.convert_from_wtf(wtf_doc)

Deepgram
~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import DeepgramConverter

   converter = DeepgramConverter()
   wtf_doc = converter.convert_to_wtf(deepgram_data)

   # Convert back to Deepgram format
   deepgram_output = converter.convert_from_wtf(wtf_doc)

AssemblyAI
~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import AssemblyAIConverter

   converter = AssemblyAIConverter()
   wtf_doc = converter.convert_to_wtf(assemblyai_data)

   # Convert back to AssemblyAI format
   assemblyai_output = converter.convert_from_wtf(wtf_doc)

Rev.ai
~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import RevAIConverter

   converter = RevAIConverter()
   wtf_doc = converter.convert_to_wtf(rev_ai_data)

   # Convert back to Rev.ai format
   rev_ai_output = converter.convert_from_wtf(wtf_doc)

Hugging Face Models
~~~~~~~~~~~~~~~~~~~

Canary (NVIDIA):

.. code-block:: python

   from wtf_transcript_converter.providers import CanaryConverter

   converter = CanaryConverter()
   wtf_doc = converter.convert_to_wtf(canary_data)

   # Convert back to Canary format
   canary_output = converter.convert_from_wtf(wtf_doc)

Parakeet (NVIDIA):

.. code-block:: python

   from wtf_transcript_converter.providers import ParakeetConverter

   converter = ParakeetConverter()
   wtf_doc = converter.convert_to_wtf(parakeet_data)

   # Convert back to Parakeet format
   parakeet_output = converter.convert_from_wtf(wtf_doc)

Validation and Error Handling
-----------------------------

Validate WTF Documents
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import validate_wtf_document

   is_valid, errors = validate_wtf_document(wtf_doc)

   if not is_valid:
       print("Validation errors:")
       for error in errors:
           print(f"  - {error}")
   else:
       print("WTF document is valid!")

Handle Conversion Errors
~~~~~~~~~~~~~~~~~~~~~~~~

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

Advanced Features
-----------------

Custom Validation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.core.validator import WTFValidator

   validator = WTFValidator()

   # Add custom validation rules
   validator.add_custom_rule("custom_rule", lambda doc: doc.transcript.confidence > 0.5)

   is_valid, errors = validator.validate(wtf_doc)

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()

   # Process multiple files
   input_files = ["file1.json", "file2.json", "file3.json"]

   for input_file in input_files:
       with open(input_file, 'r') as f:
           data = json.load(f)

       wtf_doc = converter.convert_to_wtf(data)

       # Save WTF document
       output_file = input_file.replace('.json', '.wtf.json')
       with open(output_file, 'w') as f:
           f.write(wtf_doc.model_dump_json(indent=2))

Next Steps
----------

Now that you have the basics down, explore these topics:

* :doc:`user_guide` - Comprehensive user guide
* :doc:`api_reference` - Complete API documentation
* :doc:`providers` - Provider-specific documentation
* :doc:`cross_provider_testing` - Cross-provider testing guide
* :doc:`examples` - More examples and use cases

Need Help?
----------

* Check the `GitHub Issues <https://github.com/vcon-dev/wtf-transcript-converter/issues>`_
* Join our `Discord community <https://discord.gg/vcon>`_
* Contact us at `vcon@ietf.org <mailto:vcon@ietf.org>`_
