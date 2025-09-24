Installation Guide
==================

This guide provides step-by-step instructions for installing and setting up the sphinx-linkfix project template. Choose the installation section that best fits your needs.

.. contents:: Table of Contents
   :local:
   :depth: 2

Prerequisites
-------------

Before installing the project, ensure you have the following requirements:

* **Python 3.7** (required for this project)
* **Git** for cloning the repository
* **Internet connection** for downloading dependencies

User Installation
=================

This section is for users who want to use the project template without modifying the source code.

Quick Start
-----------

1. **Clone the Repository**

    Clone the project repository from GitHub::

        git clone https://github.com/j-moralejo-pinas/sphinx-linkfix.git
        cd sphinx-linkfix

2. **Set Up Virtual Environment (Recommended)**

    While not mandatory, using a virtual environment is highly recommended to avoid dependency conflicts::

        # Using conda (recommended)
        conda create -n env_config python=3.7
        conda activate env_config

        # OR using venv
        python -m venv venv
        # On Linux/macOS:
        source venv/bin/activate
        # On Windows:
        venv\Scripts\activate

3. **Install the Package**

    Install the project and its dependencies::

        pip install -e .

4. **Verify Installation**

    Test that the installation was successful::

        python -c "import sphinx_linkfix; print('Installation successful!')"

Docker Installation (Alternative)
==================================

If you prefer to use Docker instead of a local Python installation, you can run the project in a containerized environment.

Prerequisites for Docker
-------------------------

* **Docker** and **Docker Compose** installed on your system
* **Git** for cloning the repository

Docker Setup
------------

1. **Clone the Repository**

   ::

        git clone https://github.com/j-moralejo-pinas/sphinx-linkfix.git
        cd sphinx-linkfix

2. **Build the Docker Image**

    Build the application using Docker Compose::

        docker-compose build

    This will create a Docker image with all necessary dependencies pre-installed.

3. **Verify Docker Installation**

    Test that the Docker setup works::

        docker-compose run --rm app python -c "import sphinx_linkfix; print('Docker installation successful!')"

**Docker Benefits**

* **Isolated environment** - No conflicts with your system Python
* **Consistent setup** - Same environment across different machines
* **Easy cleanup** - Remove containers when done
* **Pre-configured dependencies** - All system libraries included

Developer Installation
======================

This section is for developers who want to contribute to the project or modify the source code.

Development Setup
-----------------

1. **Clone and Navigate**

   ::

        git clone https://github.com/j-moralejo-pinas/sphinx-linkfix.git
        cd sphinx-linkfix

2. **Set Up Development Environment**

    Create a virtual environment (recommended)::

        conda create -n sphinx-linkfix-dev python=3.7
        conda activate sphinx-linkfix-dev

3. **Install in Development Mode**

    Install the package with development dependencies::

        pip install -e ".[dev,docs]"

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

4. **Set Up Pre-commit Hooks**

    Install pre-commit hooks to ensure code quality::

        pre-commit install

5. **Configure Type Checking**

    Link your development environment to Pyright for proper type checking. Create a ``pyrightconfig.local.json`` file in the project root::

        {
            "venvPath": "/path/to/your/conda/envs",
            "venv": "sphinx-linkfix-dev"
        }

    Replace ``/path/to/your/conda/envs`` with your actual conda environments path (e.g., ``/home/username/miniconda3/envs`` or ``/home/username/micromamba/envs``).

6. **Configure Environment**

    Set the ``PYTHONPATH`` environment variable::

        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

    Or add this to your shell profile (``~/.bashrc``, ``~/.zshrc``, etc.).

7. **Verify Installation**

    Test that the development installation was successful::

        python -c "import sphinx_linkfix; print('Development installation successful!')"
        pytest --version
        ruff --version
        pyright --version

Troubleshooting
===============

**Common Issues**

**Import Errors**

If you encounter import errors, ensure the ``PYTHONPATH`` is set correctly::

    export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

**Virtual Environment Issues**

If you have issues with virtual environments, try::

    # For conda environments
    conda info --envs  # List all environments
    conda activate sphinx-linkfix-dev  # Activate the environment

    # For venv environments
    which python  # Check which Python you're using
    pip list  # Check installed packages

**Docker Issues**

If Docker commands fail::

    # Check Docker is running
    docker --version
    docker-compose --version

    # Check Docker permissions (Linux)
    sudo usermod -aG docker $USER
    # Then log out and back in

**Getting Help**

* Check the project's GitHub issues: https://github.com/j-moralejo-pinas/sphinx-linkfix/issues
* Review the documentation for detailed usage examples
* Ensure all dependencies are correctly installed

See Also
========

- `Contributing <CONTRIBUTING.rst>`_ - How to contribute to the project
