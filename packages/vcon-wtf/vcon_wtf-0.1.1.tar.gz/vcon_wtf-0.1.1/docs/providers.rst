Provider Documentation
======================

This section provides detailed documentation for each supported transcription provider.

Overview
--------

The WTF Transcript Converter supports 6 major transcription providers, each with unique features and capabilities:

* **Whisper** (OpenAI) - High-quality speech recognition with punctuation detection
* **Deepgram** - Real-time and batch transcription with speaker diarization
* **AssemblyAI** - Advanced AI transcription with sentiment analysis and auto-chapters
* **Rev.ai** - Professional transcription services with speaker confidence
* **Canary** (NVIDIA) - Hugging Face integration for local transcription
* **Parakeet** (NVIDIA) - Hugging Face integration with transducer-based processing

Whisper (OpenAI)
----------------

Whisper is OpenAI's automatic speech recognition system trained on 680,000 hours of multilingual and multitask supervised data.

Features
~~~~~~~~

* High-quality speech recognition
* Punctuation detection
* Word-level confidence scores
* Log probability scores
* Support for 99 languages

Data Format
~~~~~~~~~~~

Whisper returns transcriptions in the following format:

.. code-block:: json

   {
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
           {
             "word": "Hello,",
             "start": 0.0,
             "end": 0.5,
             "probability": 0.99
           }
         ]
       }
     ]
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

   # Access Whisper-specific features
   print(f"Log probability: {wtf_doc.segments[0].confidence}")
   print(f"Word probabilities: {[word.confidence for word in wtf_doc.words]}")

Deepgram
--------

Deepgram provides real-time and batch transcription services with advanced features like speaker diarization and language detection.

Features
~~~~~~~~

* Real-time and batch transcription
* Speaker diarization
* Language detection
* Channel support
* Alternative transcriptions
* Word-level timestamps

Data Format
~~~~~~~~~~~

Deepgram returns transcriptions in the following format:

.. code-block:: json

   {
     "metadata": {
       "duration": 3.5,
       "language": "en-US"
     },
     "results": {
       "channels": [
         {
           "alternatives": [
             {
               "transcript": "Hello, this is a test transcription.",
               "confidence": 0.95,
               "words": [
                 {
                   "word": "Hello,",
                   "start": 0.0,
                   "end": 0.5,
                   "confidence": 0.99,
                   "speaker": 0
                 }
               ]
             }
           ]
         }
       ]
     }
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import DeepgramConverter

   converter = DeepgramConverter()
   wtf_doc = converter.convert_to_wtf(deepgram_data)

   # Access Deepgram-specific features
   print(f"Speaker count: {len(wtf_doc.speakers)}")
   print(f"Channel count: {len(deepgram_data['results']['channels'])}")

AssemblyAI
----------

AssemblyAI provides advanced AI transcription services with features like sentiment analysis, auto-chapters, and IAB content classification.

Features
~~~~~~~~

* Advanced AI transcription
* Sentiment analysis
* Auto-chapters
* IAB content classification
* Speaker diarization
* Utterance-level timestamps

Data Format
~~~~~~~~~~~

AssemblyAI returns transcriptions in the following format:

.. code-block:: json

   {
     "text": "Hello, this is a test transcription.",
     "language_code": "en_us",
     "audio_duration": 3.5,
     "confidence": 0.96,
     "words": [
       {
         "text": "Hello,",
         "start": 0,
         "end": 500,
         "confidence": 0.99
       }
     ],
     "utterances": [
       {
         "text": "Hello, this is a test transcription.",
         "start": 0,
         "end": 3500,
         "confidence": 0.96,
         "speaker": "A"
       }
     ]
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import AssemblyAIConverter

   converter = AssemblyAIConverter()
   wtf_doc = converter.convert_to_wtf(assemblyai_data)

   # Access AssemblyAI-specific features
   print(f"Utterance count: {len(assemblyai_data['utterances'])}")
   print(f"Language code: {assemblyai_data['language_code']}")

Rev.ai
------

Rev.ai provides professional transcription services with speaker confidence scores and detailed timing information.

Features
~~~~~~~~

* Professional transcription services
* Speaker confidence scores
* Detailed timing information
* Monologue-based structure
* Element-level timestamps

Data Format
~~~~~~~~~~~

Rev.ai returns transcriptions in the following format:

.. code-block:: json

   {
     "duration_seconds": 3.5,
     "monologues": [
       {
         "speaker": 0,
         "elements": [
           {
             "type": "text",
             "value": "Hello,",
             "ts": 0.0,
             "end_ts": 0.5,
             "confidence": 0.9
           }
         ]
       }
     ]
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import RevAIConverter

   converter = RevAIConverter()
   wtf_doc = converter.convert_to_wtf(rev_ai_data)

   # Access Rev.ai-specific features
   print(f"Monologue count: {len(rev_ai_data['monologues'])}")
   print(f"Duration: {rev_ai_data['duration_seconds']}s")

Canary (NVIDIA)
---------------

Canary is NVIDIA's speech recognition model available through Hugging Face, providing local transcription capabilities.

Features
~~~~~~~~

* Local transcription (no API required)
* Hugging Face integration
* High-quality speech recognition
* Word-level timestamps
* Confidence scores

Data Format
~~~~~~~~~~~

Canary returns transcriptions in the following format:

.. code-block:: json

   {
     "text": "Hello, this is a test transcription.",
     "language": "en",
     "duration": 3.5,
     "segments": [
       {
         "start": 0.0,
         "end": 3.5,
         "text": "Hello, this is a test transcription.",
         "confidence": 0.92,
         "words": [
           {
             "word": "Hello,",
             "start": 0.0,
             "end": 0.5,
             "confidence": 0.99
           }
         ]
       }
     ]
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import CanaryConverter

   converter = CanaryConverter()
   wtf_doc = converter.convert_to_wtf(canary_data)

   # Access Canary-specific features
   print(f"Model: {wtf_doc.metadata.model}")
   print(f"Provider: {wtf_doc.metadata.provider}")

Parakeet (NVIDIA)
-----------------

Parakeet is NVIDIA's transducer-based speech recognition model available through Hugging Face.

Features
~~~~~~~~

* Transducer-based processing
* Hugging Face integration
* Local transcription capabilities
* Word-level timestamps
* Confidence scores

Data Format
~~~~~~~~~~~

Parakeet returns transcriptions in the following format:

.. code-block:: json

   {
     "text": "Hello, this is a test transcription.",
     "language": "en",
     "duration": 3.5,
     "segments": [
       {
         "start": 0.0,
         "end": 3.5,
         "text": "Hello, this is a test transcription.",
         "confidence": 0.91,
         "words": [
           {
             "word": "Hello,",
             "start": 0.0,
             "end": 0.5,
             "confidence": 0.98
           }
         ]
       }
     ]
   }

Usage
~~~~~

.. code-block:: python

   from wtf_transcript_converter.providers import ParakeetConverter

   converter = ParakeetConverter()
   wtf_doc = converter.convert_to_wtf(parakeet_data)

   # Access Parakeet-specific features
   print(f"Model: {wtf_doc.metadata.model}")
   print(f"Provider: {wtf_doc.metadata.provider}")

Provider Comparison
-------------------

Feature Matrix
~~~~~~~~~~~~~~

+------------------+----------+----------+-----------+----------+----------+----------+
| Feature          | Whisper  | Deepgram | AssemblyAI| Rev.ai   | Canary   | Parakeet |
+==================+==========+==========+===========+==========+==========+==========+
| Word Timestamps  | ✅       | ✅       | ✅        | ✅       | ✅       | ✅       |
| Speaker Diarization| ❌      | ✅       | ✅        | ✅       | ❌       | ❌       |
| Confidence Scores| ✅       | ✅       | ✅        | ✅       | ✅       | ✅       |
| Punctuation      | ✅       | ✅       | ✅        | ✅       | ✅       | ✅       |
| Language Detection| ✅       | ✅       | ✅        | ❌       | ✅       | ✅       |
| Real-time        | ❌       | ✅       | ❌        | ❌       | ❌       | ❌       |
| Local Processing | ✅       | ❌       | ❌        | ❌       | ✅       | ✅       |
| API Required     | ✅       | ✅       | ✅        | ✅       | ❌       | ❌       |
+------------------+----------+----------+-----------+----------+----------+----------+

Performance Comparison
~~~~~~~~~~~~~~~~~~~~~~

+------------------+----------+----------+-----------+----------+----------+----------+
| Metric           | Whisper  | Deepgram | AssemblyAI| Rev.ai   | Canary   | Parakeet |
+==================+==========+==========+===========+==========+==========+==========+
| Accuracy         | High     | High     | High      | High     | Medium   | Medium   |
| Speed            | Medium   | Fast     | Medium    | Medium   | Slow     | Slow     |
| Cost             | Medium   | Low      | Medium    | High     | Free     | Free     |
| Setup Complexity | Low      | Low      | Low       | Low      | High     | High     |
+------------------+----------+----------+-----------+----------+----------+----------+

Choosing a Provider
-------------------

Use Cases
~~~~~~~~~

**Whisper**
* High-quality transcription needed
* Offline processing preferred
* Multiple languages required
* Budget-conscious projects

**Deepgram**
* Real-time transcription needed
* Speaker diarization required
* High-volume processing
* Cost optimization important

**AssemblyAI**
* Advanced features needed (sentiment, chapters)
* High accuracy required
* Speaker diarization needed
* Budget allows for premium features

**Rev.ai**
* Professional transcription services
* High accuracy required
* Speaker confidence important
* Budget allows for premium pricing

**Canary/Parakeet**
* Local processing required
* No API costs desired
* Hugging Face integration preferred
* Setup complexity acceptable

Best Practices
~~~~~~~~~~~~~~

1. **Test Multiple Providers**: Use cross-provider testing to compare results
2. **Consider Use Case**: Match provider features to your specific needs
3. **Monitor Performance**: Track accuracy, speed, and cost over time
4. **Handle Errors Gracefully**: Implement proper error handling for API failures
5. **Cache Results**: Store converted WTF documents to avoid re-processing
6. **Validate Output**: Always validate WTF documents after conversion

Integration Examples
~~~~~~~~~~~~~~~~~~~~

See the :doc:`examples` section for detailed integration examples with each provider.
