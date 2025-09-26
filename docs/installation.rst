==================
Installation Guide
==================

This guide provides step-by-step instructions for installing and setting up the sphinx-linkfix project template. Choose the installation section that best fits your needs.

.. contents:: Table of Contents
    :local:
    :depth: 2

Prerequisites
=============

Before installing the project, ensure you have the following requirements:

* **Python 3.9** (required for this project)
* **Git** for cloning the repository
* **Internet connection** for downloading dependencies

User Installation
=================

This section is for users who want to use the extension.

Quick Start
-----------

1. **Install the Extension**: Install the package using pip

.. code-block::

    pip install sphinx-linkfix

2. **Configure Sphinx**: In your Sphinx ``conf.py`` file, add the extension

.. code-block::

    extensions = [
        ...,
        'sphinx_linkfix',
    ]

3. **Set Configuration Options (Optional)**: You can customize the behavior of the extension by adding the following options to your ``conf.py`` file:

.. code-block:: python

    # Path prefix to strip from links (default: "docs/")
    docs_relative_path = 'docs/'

    # List of file extensions to process
    sphinx_linkfix_file_extensions = ('.rst', '.md')

Developer Installation
======================

This section is for developers who want to contribute to the project or modify the source code.

Development Setup
-----------------

1. **Clone and Navigate**

.. code-block::

    git clone https://github.com/j-moralejo-pinas/sphinx-linkfix.git
    cd sphinx-linkfix

2. **Set Up Development Environment**: Create a virtual environment (recommended)

.. code-block::

    conda create -n sphinx-linkfix-dev python=3.9
    conda activate sphinx-linkfix-dev

3. **Install in Development Mode**: Install the package with development dependencies
    This installs the project in editable mode with all development tools including:

    * ``pytest`` - Testing framework
    * ``pyright`` - Type checking
    * ``pre-commit`` - Git hooks for code quality
    * ``ruff`` - Fast Python linter and formatter
    * ``pydoclint`` - Documentation linting
    * ``docformatter`` - Documentation formatting
    * ``pytest-cov`` - Test coverage
    * ``pyupgrade`` - Code modernization
    * ``sphinx`` - Documentation generation
    * ``sphinx-autoapi`` - Automatic API documentation generation

.. code-block::

    pip install -e ".[dev,docs]"

4. **Set Up Pre-commit Hooks**: Install pre-commit hooks to ensure code quality

.. code-block::

    pre-commit install

5. **Configure Type Checking**: Link your development environment to Pyright for proper type checking. Create a ``pyrightconfig.local.json`` file in the project root

.. code-block::

    {
        "venvPath": "/path/to/your/conda/envs",
        "venv": "sphinx-linkfix-dev"
    }

.. [#f1] Replace ``/path/to/your/conda/envs`` with your actual conda environments path (e.g., ``/home/username/miniconda3/envs`` or ``/home/username/micromamba/envs``).

6. **Configure Environment**: Set the ``PYTHONPATH`` environment variable or add it to your shell profile to include the source directory (``~/.bashrc``, ``~/.zshrc``, etc.)

.. code-block::

    export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

7. **Verify Installation**: Test that the development installation was successful

.. code-block::

    python -c "import sphinx_linkfix; print('Development installation successful!')"
    pytest --version
    ruff --version
    pyright --version

Troubleshooting
===============

**Common Issues**

**Import Errors**

If you encounter import errors, ensure the ``PYTHONPATH`` is set correctly

.. code-block::

    export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

**Virtual Environment Issues**

If you have issues with virtual environments, try

.. code-block::

    # For conda environments
    conda info --envs  # List all environments
    conda activate sphinx-linkfix-dev  # Activate the environment

    # For venv environments
    which python  # Check which Python you're using
    pip list  # Check installed packages

**Getting Help**

* Check the project's GitHub issues: https://github.com/j-moralejo-pinas/sphinx-linkfix/issues
* Review the documentation for detailed usage examples
* Ensure all dependencies are correctly installed

See Also
========

- `Contributing <CONTRIBUTING.rst>`_ - How to contribute to the project
