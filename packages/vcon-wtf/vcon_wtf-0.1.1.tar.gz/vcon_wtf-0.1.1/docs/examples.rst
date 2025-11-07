Examples and Use Cases
======================

This section provides comprehensive examples and use cases for the WTF Transcript Converter library.

Basic Examples
--------------

Simple Conversion
~~~~~~~~~~~~~~~~~

Convert a Whisper transcription to WTF format:

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter

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

   # Convert to WTF
   converter = WhisperConverter()
   wtf_doc = converter.convert_to_wtf(whisper_data)

   print(f"Text: {wtf_doc.transcript.text}")
   print(f"Language: {wtf_doc.transcript.language}")
   print(f"Duration: {wtf_doc.transcript.duration}s")
   print(f"Confidence: {wtf_doc.transcript.confidence}")

Cross-Provider Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~

Convert from Whisper to Deepgram format:

.. code-block:: python

   from wtf_transcript_converter.providers import WhisperConverter, DeepgramConverter

   # Convert Whisper to WTF
   whisper_converter = WhisperConverter()
   wtf_doc = whisper_converter.convert_to_wtf(whisper_data)

   # Convert WTF to Deepgram
   deepgram_converter = DeepgramConverter()
   deepgram_data = deepgram_converter.convert_from_wtf(wtf_doc)

   print("Deepgram format:")
   print(deepgram_data)

Validation Example
~~~~~~~~~~~~~~~~~~

Validate a WTF document:

.. code-block:: python

   from wtf_transcript_converter.core.validator import validate_wtf_document

   # Validate the WTF document
   is_valid, errors = validate_wtf_document(wtf_doc)

   if is_valid:
       print("✅ WTF document is valid!")
   else:
       print("❌ WTF document has errors:")
       for error in errors:
           print(f"  - {error}")

Real-World Examples
-------------------

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple transcription files:

.. code-block:: python

   import json
   from pathlib import Path
   from wtf_transcript_converter.providers import WhisperConverter

   def process_transcription_files(input_dir, output_dir, provider="whisper"):
       """Process multiple transcription files and convert to WTF format."""

       # Create output directory
       output_path = Path(output_dir)
       output_path.mkdir(exist_ok=True)

       # Initialize converter
       if provider == "whisper":
           converter = WhisperConverter()
       elif provider == "deepgram":
           converter = DeepgramConverter()
       else:
           raise ValueError(f"Unsupported provider: {provider}")

       # Process each file
       input_path = Path(input_dir)
       for input_file in input_path.glob("*.json"):
           try:
               # Load input data
               with open(input_file, 'r', encoding='utf-8') as f:
                   data = json.load(f)

               # Convert to WTF
               wtf_doc = converter.convert_to_wtf(data)

               # Save WTF document
               output_file = output_path / f"{input_file.stem}.wtf.json"
               with open(output_file, 'w', encoding='utf-8') as f:
                   f.write(wtf_doc.model_dump_json(indent=2))

               print(f"✅ Processed: {input_file.name} -> {output_file.name}")

           except Exception as e:
               print(f"❌ Error processing {input_file.name}: {e}")

   # Usage
   process_transcription_files("input_files", "output_files", "whisper")

API Integration
~~~~~~~~~~~~~~~

Integrate with transcription APIs:

.. code-block:: python

   import asyncio
   import aiohttp
   from wtf_transcript_converter.providers import WhisperConverter, DeepgramConverter

   async def transcribe_with_multiple_providers(audio_file_path):
       """Transcribe audio using multiple providers and compare results."""

       results = {}

       # Whisper API
       async with aiohttp.ClientSession() as session:
           # Upload to Whisper API
           with open(audio_file_path, 'rb') as f:
               files = {'file': f}
               async with session.post('https://api.openai.com/v1/audio/transcriptions',
                                     headers={'Authorization': f'Bearer {WHISPER_API_KEY}'},
                                     data={'model': 'whisper-1'},
                                     files=files) as response:
                   whisper_data = await response.json()

           # Convert to WTF
           whisper_converter = WhisperConverter()
           results['whisper'] = whisper_converter.convert_to_wtf(whisper_data)

       # Deepgram API
       async with aiohttp.ClientSession() as session:
           with open(audio_file_path, 'rb') as f:
               async with session.post('https://api.deepgram.com/v1/listen',
                                     headers={'Authorization': f'Token {DEEPGRAM_API_KEY}'},
                                     data=f) as response:
                   deepgram_data = await response.json()

           # Convert to WTF
           deepgram_converter = DeepgramConverter()
           results['deepgram'] = deepgram_converter.convert_to_wtf(deepgram_data)

       return results

   # Usage
   async def main():
       results = await transcribe_with_multiple_providers("audio.wav")

       for provider, wtf_doc in results.items():
           print(f"{provider.upper()}:")
           print(f"  Text: {wtf_doc.transcript.text}")
           print(f"  Confidence: {wtf_doc.transcript.confidence}")
           print()

   asyncio.run(main())

Quality Analysis
~~~~~~~~~~~~~~~~

Analyze transcription quality:

.. code-block:: python

   from wtf_transcript_converter.core.validator import validate_wtf_document
   from wtf_transcript_converter.cross_provider.quality import QualityComparator

   def analyze_transcription_quality(wtf_doc):
       """Analyze the quality of a transcription."""

       # Basic validation
       is_valid, errors = validate_wtf_document(wtf_doc)

       # Quality metrics
       quality_metrics = {
           'is_valid': is_valid,
           'validation_errors': errors,
           'overall_confidence': wtf_doc.transcript.confidence,
           'duration': wtf_doc.transcript.duration,
           'word_count': len(wtf_doc.words) if wtf_doc.words else 0,
           'segment_count': len(wtf_doc.segments),
           'speaker_count': len(wtf_doc.speakers) if wtf_doc.speakers else 0
       }

       # Word-level analysis
       if wtf_doc.words:
           word_confidences = [word.confidence for word in wtf_doc.words]
           quality_metrics.update({
               'avg_word_confidence': sum(word_confidences) / len(word_confidences),
               'min_word_confidence': min(word_confidences),
               'max_word_confidence': max(word_confidences),
               'low_confidence_words': sum(1 for c in word_confidences if c < 0.5),
               'high_confidence_words': sum(1 for c in word_confidences if c > 0.9)
           })

       # Quality assessment
       if quality_metrics['overall_confidence'] > 0.9:
           quality_metrics['quality_rating'] = 'Excellent'
       elif quality_metrics['overall_confidence'] > 0.8:
           quality_metrics['quality_rating'] = 'Good'
       elif quality_metrics['overall_confidence'] > 0.7:
           quality_metrics['quality_rating'] = 'Fair'
       else:
           quality_metrics['quality_rating'] = 'Poor'

       return quality_metrics

   # Usage
   quality = analyze_transcription_quality(wtf_doc)
   print(f"Quality Rating: {quality['quality_rating']}")
   print(f"Overall Confidence: {quality['overall_confidence']:.2f}")
   print(f"Word Count: {quality['word_count']}")

Cross-Provider Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~

Compare results across providers:

.. code-block:: python

   from wtf_transcript_converter.cross_provider import (
       CrossProviderConsistencyTester,
       PerformanceBenchmark,
       QualityComparator
   )

   def compare_providers(sample_data):
       """Compare transcription results across multiple providers."""

       # Initialize testers
       consistency_tester = CrossProviderConsistencyTester()
       performance_benchmark = PerformanceBenchmark()
       quality_comparator = QualityComparator()

       # Test consistency
       consistency_report = consistency_tester.generate_consistency_report(
           "sample_audio.wav",
           ["whisper", "deepgram", "assemblyai"],
           {}
       )

       # Test performance
       performance_metrics = performance_benchmark.benchmark_all_providers(sample_data, 3)
       performance_analysis = performance_benchmark.analyze_performance(performance_metrics)

       # Test quality
       wtf_docs = {}
       for provider in ["whisper", "deepgram", "assemblyai"]:
           wtf_docs[provider] = quality_comparator.convert_to_wtf(provider, sample_data)
       quality_comparison = quality_comparator.compare_qualities(wtf_docs)

       # Generate summary
       summary = {
           'consistency': {
               'most_consistent': None,
               'inconsistencies': []
           },
           'performance': {
               'fastest': performance_analysis['fastest_converter'],
               'most_efficient': performance_analysis['lowest_memory']
           },
           'quality': {
               'best_quality': quality_comparison['comparison_results']['best_overall_confidence_provider'],
               'quality_scores': {}
           }
       }

       # Analyze consistency
       for comparison, data in consistency_report['comparisons'].items():
           if not data['transcript_text_match']:
               summary['consistency']['inconsistencies'].append(comparison)

       # Analyze quality
       for provider, analysis in quality_comparison['analyzed_docs'].items():
           summary['quality']['quality_scores'][provider] = analysis['overall_confidence']

       return summary

   # Usage
   comparison = compare_providers(sample_data)
   print("Provider Comparison Summary:")
   print(f"Fastest: {comparison['performance']['fastest']}")
   print(f"Best Quality: {comparison['quality']['best_quality']}")
   print(f"Inconsistencies: {len(comparison['consistency']['inconsistencies'])}")

Advanced Examples
-----------------

Custom Validation Rules
~~~~~~~~~~~~~~~~~~~~~~~

Create custom validation rules:

.. code-block:: python

   from wtf_transcript_converter.core.validator import WTFValidator

   def create_custom_validator():
       """Create a validator with custom rules."""

       validator = WTFValidator()

       # Add custom rules
       validator.add_custom_rule(
           "min_confidence",
           lambda doc: doc.transcript.confidence >= 0.8,
           "Confidence must be at least 0.8"
       )

       validator.add_custom_rule(
           "max_duration",
           lambda doc: doc.transcript.duration <= 3600,  # 1 hour
           "Duration must not exceed 1 hour"
       )

       validator.add_custom_rule(
           "min_word_count",
           lambda doc: len(doc.words) >= 5 if doc.words else True,
           "Must have at least 5 words"
       )

       validator.add_custom_rule(
           "language_check",
           lambda doc: doc.transcript.language in ["en", "es", "fr", "de"],
           "Language must be supported"
       )

       return validator

   # Usage
   custom_validator = create_custom_validator()
   is_valid, errors = custom_validator.validate(wtf_doc)

   if not is_valid:
       print("Custom validation failed:")
       for error in errors:
           print(f"  - {error}")

Error Handling and Recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement robust error handling:

.. code-block:: python

   import logging
   from wtf_transcript_converter.providers import WhisperConverter, DeepgramConverter
   from wtf_transcript_converter.exceptions import ConversionError, ValidationError

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   def robust_conversion(data, primary_provider="whisper", fallback_providers=None):
       """Convert data with fallback providers."""

       if fallback_providers is None:
           fallback_providers = ["deepgram", "assemblyai"]

       # Try primary provider first
       try:
           if primary_provider == "whisper":
               converter = WhisperConverter()
           elif primary_provider == "deepgram":
               converter = DeepgramConverter()
           else:
               raise ValueError(f"Unsupported provider: {primary_provider}")

           wtf_doc = converter.convert_to_wtf(data)

           # Validate result
           is_valid, errors = validate_wtf_document(wtf_doc)
           if not is_valid:
               raise ValidationError(f"Validation failed: {errors}")

           logger.info(f"Successfully converted with {primary_provider}")
           return wtf_doc, primary_provider

       except Exception as e:
           logger.warning(f"Primary provider {primary_provider} failed: {e}")

           # Try fallback providers
           for fallback_provider in fallback_providers:
               try:
                   if fallback_provider == "whisper":
                       converter = WhisperConverter()
                   elif fallback_provider == "deepgram":
                       converter = DeepgramConverter()
                   else:
                       continue

                   wtf_doc = converter.convert_to_wtf(data)

                   # Validate result
                   is_valid, errors = validate_wtf_document(wtf_doc)
                   if not is_valid:
                       raise ValidationError(f"Validation failed: {errors}")

                   logger.info(f"Successfully converted with fallback provider {fallback_provider}")
                   return wtf_doc, fallback_provider

               except Exception as fallback_error:
                   logger.warning(f"Fallback provider {fallback_provider} failed: {fallback_error}")
                   continue

           # All providers failed
           raise ConversionError("All providers failed to convert the data")

   # Usage
   try:
       wtf_doc, used_provider = robust_conversion(data)
       print(f"Conversion successful using {used_provider}")
   except ConversionError as e:
       print(f"All conversions failed: {e}")

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

Optimize for performance:

.. code-block:: python

   import asyncio
   import aiofiles
   from concurrent.futures import ThreadPoolExecutor
   from wtf_transcript_converter.providers import WhisperConverter

   async def async_batch_processing(file_paths, max_workers=4):
       """Process multiple files asynchronously."""

       async def process_file(file_path):
           """Process a single file."""
           try:
               # Read file
               async with aiofiles.open(file_path, 'r') as f:
                   data = json.loads(await f.read())

               # Convert in thread pool to avoid blocking
               loop = asyncio.get_event_loop()
               with ThreadPoolExecutor() as executor:
                   converter = WhisperConverter()
                   wtf_doc = await loop.run_in_executor(
                       executor, converter.convert_to_wtf, data
                   )

               # Save result
               output_path = file_path.replace('.json', '.wtf.json')
               async with aiofiles.open(output_path, 'w') as f:
                   await f.write(wtf_doc.model_dump_json(indent=2))

               return file_path, True, None

           except Exception as e:
               return file_path, False, str(e)

       # Process files concurrently
       tasks = [process_file(path) for path in file_paths]
       results = await asyncio.gather(*tasks, return_exceptions=True)

       # Process results
       successful = 0
       failed = 0

       for result in results:
           if isinstance(result, Exception):
               failed += 1
               logger.error(f"Task failed with exception: {result}")
           else:
               file_path, success, error = result
               if success:
                   successful += 1
                   logger.info(f"✅ Processed: {file_path}")
               else:
                   failed += 1
                   logger.error(f"❌ Failed: {file_path} - {error}")

       return successful, failed

   # Usage
   async def main():
       file_paths = ["file1.json", "file2.json", "file3.json"]
       successful, failed = await async_batch_processing(file_paths)
       print(f"Processed {successful} files successfully, {failed} failed")

   asyncio.run(main())

Integration Examples
--------------------

Web API Integration
~~~~~~~~~~~~~~~~~~~

Create a web API for transcription conversion:

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   from wtf_transcript_converter.providers import WhisperConverter, DeepgramConverter
   from wtf_transcript_converter.core.validator import validate_wtf_document

   app = FastAPI(title="WTF Transcript Converter API")

   class ConversionRequest(BaseModel):
       data: dict
       provider: str
       validate: bool = True

   class ConversionResponse(BaseModel):
       success: bool
       wtf_document: dict = None
       errors: list = None

   @app.post("/convert", response_model=ConversionResponse)
   async def convert_transcription(request: ConversionRequest):
       """Convert transcription data to WTF format."""

       try:
           # Initialize converter
           if request.provider == "whisper":
               converter = WhisperConverter()
           elif request.provider == "deepgram":
               converter = DeepgramConverter()
           else:
               raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

           # Convert to WTF
           wtf_doc = converter.convert_to_wtf(request.data)

           # Validate if requested
           if request.validate:
               is_valid, errors = validate_wtf_document(wtf_doc)
               if not is_valid:
                   return ConversionResponse(
                       success=False,
                       errors=errors
                   )

           return ConversionResponse(
               success=True,
               wtf_document=wtf_doc.model_dump()
           )

       except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))

   @app.get("/providers")
   async def list_providers():
       """List available providers."""
       return {
           "providers": [
               {"name": "whisper", "description": "OpenAI Whisper"},
               {"name": "deepgram", "description": "Deepgram API"},
               {"name": "assemblyai", "description": "AssemblyAI API"},
               {"name": "rev-ai", "description": "Rev.ai API"},
               {"name": "canary", "description": "NVIDIA Canary"},
               {"name": "parakeet", "description": "NVIDIA Parakeet"}
           ]
       }

Database Integration
~~~~~~~~~~~~~~~~~~~~

Store and retrieve WTF documents:

.. code-block:: python

   import sqlite3
   from datetime import datetime
   from wtf_transcript_converter.core.models import WTFDocument

   class WTFDatabase:
       """Database interface for WTF documents."""

       def __init__(self, db_path="wtf_documents.db"):
           self.db_path = db_path
           self.init_database()

       def init_database(self):
           """Initialize the database schema."""
           with sqlite3.connect(self.db_path) as conn:
               conn.execute("""
                   CREATE TABLE IF NOT EXISTS wtf_documents (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       provider TEXT NOT NULL,
                       model TEXT,
                       language TEXT,
                       duration REAL,
                       confidence REAL,
                       word_count INTEGER,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       wtf_data TEXT NOT NULL
                   )
               """)

       def store_wtf_document(self, wtf_doc: WTFDocument, provider: str):
           """Store a WTF document in the database."""

           with sqlite3.connect(self.db_path) as conn:
               conn.execute("""
                   INSERT INTO wtf_documents
                   (provider, model, language, duration, confidence, word_count, wtf_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
               """, (
                   provider,
                   wtf_doc.metadata.model if wtf_doc.metadata else None,
                   wtf_doc.transcript.language,
                   wtf_doc.transcript.duration,
                   wtf_doc.transcript.confidence,
                   len(wtf_doc.words) if wtf_doc.words else 0,
                   wtf_doc.model_dump_json()
               ))

       def get_wtf_document(self, document_id: int) -> WTFDocument:
           """Retrieve a WTF document from the database."""

           with sqlite3.connect(self.db_path) as conn:
               cursor = conn.execute(
                   "SELECT wtf_data FROM wtf_documents WHERE id = ?",
                   (document_id,)
               )
               row = cursor.fetchone()

               if row:
                   return WTFDocument.model_validate_json(row[0])
               else:
                   raise ValueError(f"Document {document_id} not found")

       def search_documents(self, provider=None, language=None, min_confidence=None):
           """Search for documents with specific criteria."""

           query = "SELECT id, provider, language, confidence, created_at FROM wtf_documents WHERE 1=1"
           params = []

           if provider:
               query += " AND provider = ?"
               params.append(provider)

           if language:
               query += " AND language = ?"
               params.append(language)

           if min_confidence:
               query += " AND confidence >= ?"
               params.append(min_confidence)

           with sqlite3.connect(self.db_path) as conn:
               cursor = conn.execute(query, params)
               return cursor.fetchall()

   # Usage
   db = WTFDatabase()

   # Store document
   db.store_wtf_document(wtf_doc, "whisper")

   # Search documents
   results = db.search_documents(provider="whisper", min_confidence=0.9)
   for doc_id, provider, language, confidence, created_at in results:
       print(f"Document {doc_id}: {provider} ({language}) - {confidence:.2f}")

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
* :doc:`user_guide` - Comprehensive user guide
