vCon WTF Documentation
======================

Welcome to the vCon WTF documentation! This library provides comprehensive support for converting between various transcription provider formats and the standardized IETF World Transcription Format (WTF).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide
   api_reference
   providers
   cross_provider_testing
   examples
   contributing
   changelog

Overview
--------

vCon WTF is a Python library that standardizes transcription data across multiple providers. It supports bidirectional conversion between provider-specific formats and the IETF World Transcription Format (WTF), enabling interoperability and consistency in transcription workflows.

Key Features
~~~~~~~~~~~~

* **Multi-Provider Support**: Convert between 6 major transcription providers
* **Bidirectional Conversion**: Provider format ↔ WTF format
* **Cross-Provider Testing**: Consistency, performance, and quality validation
* **CLI Tool**: Rich command-line interface with progress bars
* **Comprehensive Validation**: Robust WTF format validation
* **Extensible Architecture**: Easy to add new providers

Supported Providers
~~~~~~~~~~~~~~~~~~~

* **Whisper** (OpenAI) - High-quality speech recognition
* **Deepgram** - Real-time and batch transcription
* **AssemblyAI** - Advanced AI transcription with speaker diarization
* **Rev.ai** - Professional transcription services
* **Canary** (NVIDIA) - Hugging Face integration
* **Parakeet** (NVIDIA) - Hugging Face integration

Quick Start
~~~~~~~~~~~

Install the library:

.. code-block:: bash

   pip install vcon-wtf

Convert a transcription:

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)
   print(wtf_doc.transcript.text)

Use the CLI:

.. code-block:: bash

   vcon-wtf to-wtf input.json --provider whisper --output result.wtf.json

Cross-Provider Testing:

.. code-block:: bash

   vcon-wtf cross-provider all input.json --output-dir reports/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
