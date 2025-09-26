"""Test runner for demonstrating sphinx-linkfix extension with real examples."""

from __future__ import annotations

import subprocess
import sys
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def create_demo_sphinx_project(base_dir: Path) -> Path:
    """Create a demo Sphinx project to test the extension."""
    project_dir = base_dir / "demo_project"
    source_dir = project_dir / "source"
    build_dir = project_dir / "build"

    # Create directories
    source_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Create Sphinx configuration
    conf_content = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

extensions = ['sphinx_linkfix.extension']

# sphinx-linkfix configuration
docs_relative_path = 'docs/'
sphinx_linkfix_extensions = ('.rst', '.md', '.txt')

# Basic Sphinx configuration
project = 'Sphinx-Linkfix Demo'
copyright = '2025, Test Author'
author = 'Test Author'

master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'basic'
html_static_path = []
"""

    (source_dir / "conf.py").write_text(conf_content.strip())

    # Create main index file with various link types
    index_content = """
Sphinx-Linkfix Demo Documentation
=================================

This demo shows how the sphinx-linkfix extension works with different types of links.

Internal Document Links (Will be rewritten)
-------------------------------------------

These links use GitHub-style relative paths that will be converted to proper Sphinx references:

- `Installation Guide <docs/installation.rst>`_
- `User Manual <./manual/usage.rst>`_
- `API Reference <source/api.rst>`_
- `Contributing Guide <docs/contributing.rst#getting-started>`_

Cross-references within the same document tree:

- `Installation Guide with anchor <docs/installation.rst#requirements>`_
- `Usage examples <manual/usage.rst#examples>`_

External Links (Will remain unchanged)
--------------------------------------

These external links should not be modified by the extension:

- `Sphinx Documentation <https://www.sphinx-doc.org/>`_
- `GitHub Repository <https://github.com/example/repo>`_
- `Python.org <http://python.org>`_
- `Email Contact <mailto:admin@example.com>`_

Non-matching File Types (Will remain unchanged)
-----------------------------------------------

These links point to files that don't match our configured extensions:

- `Python Script <scripts/build.py>`_
- `CSS Stylesheet <_static/style.css>`_
- `JavaScript File <_static/app.js>`_
- `Image File <images/logo.png>`_

Table of Contents
-----------------

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation
    manual/usage
    api
    contributing

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

    (source_dir / "index.rst").write_text(index_content.strip())

    # Create installation guide
    installation_content = """
Installation Guide
==================

Requirements
------------

- Python 3.9 or higher
- Sphinx 4.0 or higher

Installation Steps
------------------

1. Install the package:

    .. code-block:: bash

        pip install sphinx-linkfix

2. Add to your Sphinx configuration:

    .. code-block:: python

        extensions = ['sphinx_linkfix.extension']

Configuration
-------------

You can customize the extension behavior:

.. code-block:: python

    # Path prefix to strip from links (default: "docs/")
    docs_relative_path = 'docs/'

    # File extensions to process
    sphinx_linkfix_extensions = ('.rst', '.md', '.txt')

For more details, see the `usage manual <./usage.rst>`_.
"""

    (source_dir / "installation.rst").write_text(installation_content.strip())

    # Create usage manual in subdirectory
    manual_dir = source_dir / "manual"
    manual_dir.mkdir(exist_ok=True)

    usage_content = """
Usage Manual
============

Basic Usage
-----------

The extension automatically processes links during Sphinx builds.

Examples
--------

Before processing (in RST source):

.. code-block:: rst

    `Other document <docs/other.rst>`_
    `Section in document <./other.rst#section>`_

After processing (in HTML output):

.. code-block:: html

    <a href="other.html">Other document</a>
    <a href="other.html#section">Section in document</a>

Advanced Configuration
----------------------

See the `installation guide <../installation.rst#configuration>`_ for configuration options.
"""

    (manual_dir / "usage.rst").write_text(usage_content.strip())

    # Create API reference
    api_content = """
API Reference
=============

Extension Functions
-------------------

.. py:function:: _is_external(href: str) -> bool

    Check if a given href is an external link.

    :param href: The URL to check
    :type href: str
    :returns: True if the URL is external, False otherwise
    :rtype: bool

.. py:function:: _strip_prefixes(path_str: str, prefixes: tuple[str, ...]) -> str

    Remove leading folder prefixes from a path string.

    :param path_str: The path string to modify
    :type path_str: str
    :param prefixes: A tuple of prefixes to remove
    :type prefixes: tuple[str, ...]
    :returns: The modified path string with prefixes removed
    :rtype: str

Extension Class
---------------

.. py:class:: RstLinkRewriter

    Post-transform to rewrite internal links in reStructuredText files.

    .. py:method:: run() -> None

        Rewrite internal links in the document.

Configuration
-------------

For configuration details, see `installation <../installation.rst>`_.
"""

    (source_dir / "api.rst").write_text(api_content.strip())

    # Create contributing guide
    contributing_content = """
Contributing Guide
==================

Getting Started
---------------

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

Development Setup
-----------------

See the `installation guide <./installation.rst>`_ for basic setup.

For development, also install:

.. code-block:: bash

    pip install -e .[dev]

Testing
-------

Run the test suite:

.. code-block:: bash

    pytest

The tests include both unit tests and integration tests that build real Sphinx documentation.

For more information, see the `API documentation <./api.rst>`_.
"""

    (source_dir / "contributing.rst").write_text(contributing_content.strip())

    return project_dir


def build_demo_project(project_dir: Path) -> bool:
    """Build the demo project and return True if successful."""
    source_dir = project_dir / "source"
    build_dir = project_dir / "build"

    try:
        # Build HTML documentation
        result = subprocess.run(  # noqa: S603
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "html",
                "-W",  # Treat warnings as errors
                str(source_dir),
                str(build_dir / "html"),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            logger.info("Sphinx build failed with return code %s", result.returncode)
            logger.info("STDOUT: %s", result.stdout)
            logger.info("STDERR: %s", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.exception("Sphinx build timed out after 60 seconds")
        return False
    except Exception as _:
        logger.exception("Error during build")
        return False
    else:
        return True


def verify_link_rewriting(project_dir: Path) -> list[str]:
    """Verify that links were rewritten correctly and return any issues found."""
    build_dir = project_dir / "build" / "html"
    issues = []

    # Check index.html
    index_html_path = build_dir / "index.html"
    if not index_html_path.exists():
        issues.append("index.html was not generated")
        return issues

    index_html = index_html_path.read_text()

    # Verify internal links were rewritten
    expected_rewrites = [
        ("docs/installation.rst", "installation.html"),
        ("./manual/usage.rst", "manual/usage.html"),
        ("source/api.rst", "api.html"),
        ("docs/contributing.rst#getting-started", "contributing.html#getting-started"),
        ("docs/installation.rst#requirements", "installation.html#requirements"),
        ("manual/usage.rst#examples", "manual/usage.html#examples"),
    ]

    for original, expected in expected_rewrites:
        if original in index_html:
            issues.append(f"Original link '{original}' still found in HTML")
        if expected not in index_html:
            issues.append(f"Expected rewritten link '{expected}' not found in HTML")

    # Verify external links remain unchanged (may be URL-encoded)
    external_links = [
        "https://www.sphinx-doc.org/",
        "https://github.com/example/repo",
        "http://python.org",
    ]

    issues.extend(
        f"External link '{link}' was modified or removed"
        for link in external_links
        if link not in index_html
    )

    # Check for mailto link (may be URL-encoded by Sphinx)
    if "mailto:" not in index_html:
        issues.append("Email mailto link was removed completely")

    # Verify non-matching files remain unchanged
    non_matching_files = [
        "scripts/build.py",
        "_static/style.css",
        "_static/app.js",
        "images/logo.png",
    ]

    issues.extend(
        f"Non-matching file link '{file_link}' was modified or removed"
        for file_link in non_matching_files
        if file_link not in index_html
    )

    return issues


if __name__ == "__main__":
    """Run the demo to test the extension."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.info("Creating demo Sphinx project...")
        project_dir = create_demo_sphinx_project(temp_path)

        logger.info("Building documentation...")
        if build_demo_project(project_dir):
            logger.info("✓ Build successful")

            logger.info("Verifying link rewriting...")
            issues = verify_link_rewriting(project_dir)

            if not issues:
                logger.info("✓ All links rewritten correctly!")
                logger.info("Demo project created at: %s", project_dir)
                logger.info(
                    "View the HTML output at: %s", project_dir / "build" / "html" / "index.html"
                )
            else:
                logger.info("✗ Issues found with link rewriting:")
                for issue in issues:
                    logger.info("  - %s", issue)
        else:
            logger.info("✗ Build failed")
            sys.exit(1)
