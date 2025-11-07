API Reference
=============

This section provides comprehensive documentation for the WTF Transcript Converter API.

Core Models
-----------

.. automodule:: wtf_transcript_converter.core.models
   :members:
   :undoc-members:
   :show-inheritance:

WTFDocument
~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFDocument
   :members:
   :special-members: __init__
   :no-index:

WTFTranscript
~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFTranscript
   :members:
   :special-members: __init__
   :no-index:

WTFSegment
~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFSegment
   :members:
   :special-members: __init__
   :no-index:

WTFWord
~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFWord
   :members:
   :special-members: __init__
   :no-index:

WTFMetadata
~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFMetadata
   :members:
   :special-members: __init__
   :no-index:

WTFAudio
~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFAudio
   :members:
   :special-members: __init__
   :no-index:

WTFQuality
~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFQuality
   :members:
   :special-members: __init__
   :no-index:

WTFExtensions
~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.models.WTFExtensions
   :members:
   :special-members: __init__
   :no-index:

Core Validator
--------------

.. automodule:: wtf_transcript_converter.core.validator
   :members:
   :undoc-members:
   :show-inheritance:

WTFValidator
~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.validator.WTFValidator
   :members:
   :special-members: __init__

Core Converter
--------------

.. automodule:: wtf_transcript_converter.core.converter
   :members:
   :undoc-members:
   :show-inheritance:

BaseProviderConverter
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.core.converter.BaseProviderConverter
   :members:
   :special-members: __init__
   :no-index:

Provider Converters
-------------------

Whisper Converter
~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.whisper
   :members:
   :undoc-members:
   :show-inheritance:

WhisperConverter
~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.whisper.WhisperConverter
   :members:
   :special-members: __init__
   :no-index:

Deepgram Converter
~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.deepgram
   :members:
   :undoc-members:
   :show-inheritance:

DeepgramConverter
~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.deepgram.DeepgramConverter
   :members:
   :special-members: __init__
   :no-index:

AssemblyAI Converter
~~~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.assemblyai
   :members:
   :undoc-members:
   :show-inheritance:

AssemblyAIConverter
~~~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.assemblyai.AssemblyAIConverter
   :members:
   :special-members: __init__
   :no-index:

Rev.ai Converter
~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.rev_ai
   :members:
   :undoc-members:
   :show-inheritance:

RevAIConverter
~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.rev_ai.RevAIConverter
   :members:
   :special-members: __init__
   :no-index:

Canary Converter
~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.canary
   :members:
   :undoc-members:
   :show-inheritance:

CanaryConverter
~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.canary.CanaryConverter
   :members:
   :special-members: __init__
   :no-index:

Parakeet Converter
~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.providers.parakeet
   :members:
   :undoc-members:
   :show-inheritance:

ParakeetConverter
~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.providers.parakeet.ParakeetConverter
   :members:
   :special-members: __init__
   :no-index:

Cross-Provider Testing
----------------------

Consistency Testing
~~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.cross_provider.consistency
   :members:
   :undoc-members:
   :show-inheritance:

CrossProviderConsistencyTester
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.cross_provider.consistency.CrossProviderConsistencyTester
   :members:
   :special-members: __init__
   :no-index:

Performance Benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.cross_provider.performance
   :members:
   :undoc-members:
   :show-inheritance:

PerformanceBenchmark
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.cross_provider.performance.PerformanceBenchmark
   :members:
   :special-members: __init__
   :no-index:

Quality Comparison
~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.cross_provider.quality
   :members:
   :undoc-members:
   :show-inheritance:

QualityComparator
~~~~~~~~~~~~~~~~~

.. autoclass:: wtf_transcript_converter.cross_provider.quality.QualityComparator
   :members:
   :special-members: __init__
   :no-index:

Utilities
---------

Confidence Utils
~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.utils.confidence_utils
   :members:
   :undoc-members:
   :show-inheritance:

Language Utils
~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.utils.language_utils
   :members:
   :undoc-members:
   :show-inheritance:

Time Utils
~~~~~~~~~~

.. automodule:: wtf_transcript_converter.utils.time_utils
   :members:
   :undoc-members:
   :show-inheritance:

Command Line Interface
----------------------

Main CLI
~~~~~~~~

.. automodule:: wtf_transcript_converter.cli.main
   :members:
   :undoc-members:
   :show-inheritance:

Cross-Provider CLI
~~~~~~~~~~~~~~~~~~

.. automodule:: wtf_transcript_converter.cli.cross_provider
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: wtf_transcript_converter.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

ConversionError
~~~~~~~~~~~~~~~

.. autoexception:: wtf_transcript_converter.exceptions.ConversionError

ValidationError
~~~~~~~~~~~~~~~

.. autoexception:: wtf_transcript_converter.exceptions.ValidationError

ProviderError
~~~~~~~~~~~~~

.. autoexception:: wtf_transcript_converter.exceptions.ProviderError
