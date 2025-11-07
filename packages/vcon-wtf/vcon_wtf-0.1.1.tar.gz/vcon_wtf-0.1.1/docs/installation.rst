Installation
============

vCon WTF can be installed via pip or from source.

Prerequisites
-------------

* Python 3.10 or higher (3.12 recommended)
* pip or uv package manager

Installation Methods
--------------------

Install from PyPI
~~~~~~~~~~~~~~~~~

The recommended way to install vCon WTF is using pip:

.. code-block:: bash

   pip install vcon-wtf

Or using uv for faster installation:

.. code-block:: bash

   uv add vcon-wtf

Install with Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For integration testing with real API providers:

.. code-block:: bash

   pip install vcon-wtf[integration]

For development dependencies:

.. code-block:: bash

   pip install vcon-wtf[dev]

Install from Source
~~~~~~~~~~~~~~~~~~~

Clone the repository and install in development mode:

.. code-block:: bash

   git clone https://github.com/vcon-dev/wtf-transcript-converter.git
   cd wtf-transcript-converter
   pip install -e .

For development with all dependencies:

.. code-block:: bash

   pip install -e ".[dev,integration]"

Using uv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

If you're using uv for Python package management:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/vcon-dev/wtf-transcript-converter.git
   cd wtf-transcript-converter

   # Install in development mode
   uv sync --dev

   # For integration testing
   uv sync --dev --group integration

Verification
------------

Verify the installation by running:

.. code-block:: bash

   vcon-wtf --help

You should see the help output for the vCon WTF CLI.

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

* `pydantic <https://pydantic.dev/>`_ - Data validation and settings management
* `click <https://click.palletsprojects.com/>`_ - Command-line interface creation
* `rich <https://rich.readthedocs.io/>`_ - Rich text and beautiful formatting
* `jsonschema <https://python-jsonschema.readthedocs.io/>`_ - JSON schema validation
* `python-dateutil <https://dateutil.readthedocs.io/>`_ - Date/time utilities

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

Integration Testing
^^^^^^^^^^^^^^^^^^^

* `openai <https://github.com/openai/openai-python>`_ - OpenAI API client
* `deepgram-sdk <https://github.com/deepgram/deepgram-python-sdk>`_ - Deepgram API client
* `assemblyai <https://github.com/AssemblyAI/assemblyai-python-sdk>`_ - AssemblyAI API client
* `rev-ai <https://github.com/revdotcom/revai-python-sdk>`_ - Rev.ai API client
* `transformers <https://huggingface.co/docs/transformers/>`_ - Hugging Face transformers
* `torch <https://pytorch.org/>`_ - PyTorch for ML models
* `datasets <https://huggingface.co/docs/datasets/>`_ - Hugging Face datasets
* `librosa <https://librosa.org/>`_ - Audio processing
* `soundfile <https://pysoundfile.readthedocs.io/>`_ - Audio file I/O
* `psutil <https://psutil.readthedocs.io/>`_ - System monitoring

Development
^^^^^^^^^^^

* `pytest <https://pytest.org/>`_ - Testing framework
* `pytest-cov <https://pytest-cov.readthedocs.io/>`_ - Coverage plugin
* `black <https://black.readthedocs.io/>`_ - Code formatting
* `isort <https://pycqa.github.io/isort/>`_ - Import sorting
* `flake8 <https://flake8.pycqa.org/>`_ - Linting
* `mypy <https://mypy.readthedocs.io/>`_ - Type checking
* `bandit <https://bandit.readthedocs.io/>`_ - Security linting
* `safety <https://pyup.io/safety/>`_ - Dependency vulnerability scanning

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

Import Errors
^^^^^^^^^^^^^

If you encounter import errors, ensure you're using the correct Python version:

.. code-block:: bash

   python --version  # Should be 3.10 or higher

Permission Errors
^^^^^^^^^^^^^^^^^

If you encounter permission errors during installation, try using a virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install vcon-wtf

CLI Not Found
^^^^^^^^^^^^^

If the `vcon-wtf` command is not found, ensure the package is properly installed:

.. code-block:: bash

   pip show vcon-wtf
   which vcon-wtf  # On Windows: where vcon-wtf

Getting Help
------------

If you encounter issues during installation:

1. Check the `GitHub Issues <https://github.com/vcon-dev/wtf-transcript-converter/issues>`_
2. Review the `troubleshooting section <troubleshooting.html>`_
3. Join our `Discord community <https://discord.gg/vcon>`_
4. Contact the development team at `vcon@ietf.org <mailto:vcon@ietf.org>`_
