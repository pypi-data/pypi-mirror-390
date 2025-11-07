Cross-Provider Testing
======================

The WTF Transcript Converter includes a comprehensive cross-provider testing framework that allows you to compare consistency, performance, and quality across all supported transcription providers.

Overview
--------

Cross-provider testing helps you:

* **Validate Consistency**: Ensure all providers produce similar results
* **Benchmark Performance**: Compare speed and resource usage
* **Assess Quality**: Evaluate accuracy and completeness
* **Make Informed Decisions**: Choose the best provider for your use case

Testing Framework
-----------------

The framework includes three main testing modules:

* **Consistency Testing**: Compare output consistency across providers
* **Performance Benchmarking**: Measure speed and resource usage
* **Quality Comparison**: Analyze accuracy and completeness

Consistency Testing
-------------------

Purpose
~~~~~~~

Consistency testing validates that all providers produce similar results when given the same input data. This helps identify:

* Format differences between providers
* Data quality variations
* Provider-specific limitations

Usage
~~~~~

Python API:

.. code-block:: python

   from wtf_transcript_converter.cross_provider.consistency import CrossProviderConsistencyTester

   tester = CrossProviderConsistencyTester()

   # Test consistency across all providers
   report = tester.generate_consistency_report(
       audio_file_path="test_audio.wav",
       providers_to_test=["whisper", "deepgram", "assemblyai"],
       api_keys={"whisper": "your_key", "deepgram": "your_key"}
   )

   print(f"Consistency report: {report}")

CLI:

.. code-block:: bash

   # Test consistency
   vcon-wtf cross-provider consistency input.json --verbose

   # Save report to file
   vcon-wtf cross-provider consistency input.json --output consistency_report.json

Report Structure
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "audio_file": "test_audio.wav",
     "provider_results": {
       "whisper": {
         "status": "success",
         "errors": [],
         "wtf_doc_summary": {
           "text_len": 150,
           "duration": 10.5,
           "segments_count": 3,
           "words_count": 25,
           "confidence": 0.95
         }
       }
     },
     "comparisons": {
       "whisper_vs_deepgram": {
         "transcript_text_match": true,
         "duration_match": true,
         "num_segments_diff": 0,
         "avg_confidence_diff": 0.02
       }
     }
   }

Performance Benchmarking
------------------------

Purpose
~~~~~~~

Performance benchmarking measures the speed and resource usage of each provider's conversion process. This helps you:

* Choose the fastest provider for your use case
* Optimize resource usage
* Identify performance bottlenecks

Usage
~~~~~

Python API:

.. code-block:: python

   from wtf_transcript_converter.cross_provider.performance import PerformanceBenchmark

   benchmark = PerformanceBenchmark()

   # Benchmark all providers
   all_metrics = benchmark.benchmark_all_providers(sample_data, iterations=5)

   # Analyze results
   analysis = benchmark.analyze_performance(all_metrics)
   report = benchmark.generate_performance_report(all_metrics, analysis)

   print(report)

CLI:

.. code-block:: bash

   # Benchmark performance
   vcon-wtf cross-provider performance input.json --iterations 5

   # Save report to file
   vcon-wtf cross-provider performance input.json --output performance_report.json

Metrics Collected
~~~~~~~~~~~~~~~~~

* **Conversion Time**: Time taken to convert data
* **Memory Usage**: Peak memory consumption
* **CPU Usage**: Average CPU utilization
* **Output Size**: Size of the resulting WTF document

Report Structure
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "metrics": {
       "whisper": {
         "provider": "whisper",
         "conversion_time": 0.045,
         "memory_usage_mb": 25.3,
         "cpu_usage_percent": 15.2,
         "wtf_doc_size_kb": 2.1,
         "success": true
       }
     },
     "analysis": {
       "fastest_converter": "whisper",
       "lowest_memory": "deepgram",
       "lowest_cpu": "assemblyai",
       "smallest_wtf_doc": "whisper"
     }
   }

Quality Comparison
------------------

Purpose
~~~~~~~

Quality comparison analyzes the accuracy and completeness of transcriptions from different providers. This helps you:

* Identify the most accurate provider
* Understand quality trade-offs
* Make informed decisions about provider selection

Usage
~~~~~

Python API:

.. code-block:: python

   from wtf_transcript_converter.cross_provider.quality import QualityComparator

   comparator = QualityComparator()

   # Compare quality across providers
   wtf_docs = {}
   for provider in ["whisper", "deepgram", "assemblyai"]:
       wtf_docs[provider] = comparator.convert_to_wtf(provider, sample_data)

   comparison_data = comparator.compare_qualities(wtf_docs)
   report = comparator.generate_quality_report(comparison_data)

   print(report)

CLI:

.. code-block:: bash

   # Compare quality
   vcon-wtf cross-provider quality input.json --verbose

   # Save report to file
   vcon-wtf cross-provider quality input.json --output quality_report.json

Quality Metrics
~~~~~~~~~~~~~~~

* **Overall Confidence**: Average confidence score
* **Word-Level Confidence**: Individual word confidence scores
* **Low Confidence Words**: Count of words with low confidence
* **Text Completeness**: Comparison against reference text
* **Timing Accuracy**: Validation of word and segment timing

Report Structure
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "analyzed_docs": {
       "whisper": {
         "overall_confidence": 0.95,
         "average_word_confidence": 0.92,
         "low_confidence_words_count": 2,
         "segment_count": 3,
         "word_count": 25,
         "has_words": true,
         "has_speakers": false
       }
     },
     "comparison_results": {
       "best_overall_confidence_provider": "whisper",
       "max_overall_confidence": 0.95
     }
   }

Comprehensive Testing
---------------------

Run All Tests
~~~~~~~~~~~~~

The framework provides a comprehensive testing command that runs all three test types:

CLI:

.. code-block:: bash

   # Run all cross-provider tests
   vcon-wtf cross-provider all input.json --output-dir reports/

   # With custom options
   wtf-convert cross-provider all input.json \
     --output-dir reports/ \
     --iterations 3 \
     --verbose

This generates:

* `consistency_report.json` - Consistency analysis
* `performance_report.json` - Performance benchmarks
* `quality_report.json` - Quality comparison

Python API:

.. code-block:: python

   from wtf_transcript_converter.cross_provider import (
       CrossProviderConsistencyTester,
       PerformanceBenchmark,
       QualityComparator
   )

   # Run all tests
   tester = CrossProviderConsistencyTester()
   benchmark = PerformanceBenchmark()
   comparator = QualityComparator()

   # Consistency test
   consistency_report = tester.generate_consistency_report(
       "test_audio.wav",
       ["whisper", "deepgram", "assemblyai"],
       {}
   )

   # Performance test
   performance_metrics = benchmark.benchmark_all_providers(sample_data, 3)
   performance_analysis = benchmark.analyze_performance(performance_metrics)

   # Quality test
   wtf_docs = {}
   for provider in ["whisper", "deepgram", "assemblyai"]:
       wtf_docs[provider] = comparator.convert_to_wtf(provider, sample_data)
   quality_comparison = comparator.compare_qualities(wtf_docs)

Best Practices
--------------

Test Data Selection
~~~~~~~~~~~~~~~~~~~

1. **Use Representative Data**: Test with data similar to your production use case
2. **Include Edge Cases**: Test with short, long, and complex audio
3. **Multiple Languages**: Test with different languages if applicable
4. **Quality Variations**: Test with high and low quality audio

.. code-block:: python

   # Test with different audio types
   test_files = [
       "short_audio.wav",      # < 10 seconds
       "long_audio.wav",       # > 5 minutes
       "noisy_audio.wav",      # Background noise
       "multi_speaker.wav",    # Multiple speakers
       "technical_audio.wav"   # Technical terminology
   ]

   for test_file in test_files:
       wtf-convert cross-provider all test_file --output-dir f"reports/{test_file}"

Interpreting Results
~~~~~~~~~~~~~~~~~~~~

1. **Consistency**: Look for providers that produce similar results
2. **Performance**: Consider speed vs. accuracy trade-offs
3. **Quality**: Evaluate confidence scores and completeness
4. **Cost**: Factor in API costs and processing time

.. code-block:: python

   def analyze_results(consistency_report, performance_report, quality_report):
       # Find most consistent providers
       consistent_providers = []
       for comparison, data in consistency_report["comparisons"].items():
           if data["transcript_text_match"] and data["duration_match"]:
               consistent_providers.append(comparison)

       # Find fastest provider
       fastest = performance_report["analysis"]["fastest_converter"]

       # Find highest quality provider
       best_quality = quality_report["comparison_results"]["best_overall_confidence_provider"]

       return {
           "consistent": consistent_providers,
           "fastest": fastest,
           "best_quality": best_quality
       }

Automated Testing
~~~~~~~~~~~~~~~~~

Integrate cross-provider testing into your CI/CD pipeline:

.. code-block:: yaml

   # .github/workflows/cross-provider-test.yml
   name: Cross-Provider Testing

   on:
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM

   jobs:
     cross-provider-test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.12'
         - name: Install dependencies
           run: |
             pip install vcon-wtf[integration]
         - name: Run cross-provider tests
           run: |
             vcon-wtf cross-provider all test_data/sample.wav \
               --output-dir reports/ \
               --iterations 3
         - name: Upload reports
           uses: actions/upload-artifact@v3
           with:
             name: cross-provider-reports
             path: reports/

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Provider Failures**
^^^^^^^^^^^^^^^^^^^^^

If a provider fails during testing:

.. code-block:: python

   # Check provider status
   for provider, result in report["provider_results"].items():
       if result["status"] == "failed":
           print(f"Provider {provider} failed: {result['errors']}")

**Inconsistent Results**
^^^^^^^^^^^^^^^^^^^^^^^^

If providers produce inconsistent results:

.. code-block:: python

   # Analyze differences
   for comparison, data in report["comparisons"].items():
       if not data["transcript_text_match"]:
           print(f"Inconsistent text: {comparison}")
           print(f"Text length difference: {data['transcript_text_len_diff']}")

**Performance Issues**
^^^^^^^^^^^^^^^^^^^^^^

If performance is poor:

.. code-block:: python

   # Check performance metrics
   for provider, metrics in performance_report["metrics"].items():
       if metrics["conversion_time"] > 1.0:  # > 1 second
           print(f"Slow provider: {provider} ({metrics['conversion_time']}s)")

**Quality Issues**
^^^^^^^^^^^^^^^^^^

If quality is poor:

.. code-block:: python

   # Check quality metrics
   for provider, analysis in quality_report["analyzed_docs"].items():
       if analysis["overall_confidence"] < 0.8:
           print(f"Low quality provider: {provider} ({analysis['overall_confidence']})")

Getting Help
------------

* **Documentation**: Check the full documentation
* **GitHub Issues**: Report bugs and request features
* **Discord Community**: Join our Discord for support
* **Email Support**: Contact us at vcon@ietf.org

Next Steps
----------

* :doc:`examples` - More examples and use cases
* :doc:`api_reference` - Complete API documentation
* :doc:`providers` - Provider-specific documentation
