"""Integration tests using sphinx.cmd.build to test the extension in real scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


class TestSphinxLinkfixIntegration:
    """Integration tests that build real Sphinx documentation."""

    def test_basic_link_rewriting_integration(self, tmp_path: Path) -> None:
        """Test basic link rewriting with a real Sphinx build."""
        # Import at function level to avoid import error if sphinx not available
        build_main = pytest.importorskip("sphinx.cmd.build").build_main

        source_dir = tmp_path / "source"
        build_dir = tmp_path / "build"
        source_dir.mkdir()
        build_dir.mkdir()

        # Create Sphinx configuration
        (source_dir / "conf.py").write_text(
            """\
extensions = ['sphinx_linkfix']
sphinx_linkfix_strip_prefixes = ('docs/', './', 'source/')
sphinx_linkfix_extensions = ('.rst', '.md', '.txt')
project = 'Test Project'
master_doc = 'index'
html_theme = 'basic'
"""
        )

        # Create test documents
        (source_dir / "index.rst").write_text(
            """\
Test Documentation
==================

Links that should be rewritten:

- `Guide <docs/guide.rst>`_
- `Tutorial <./tutorial.rst>`_
- `API <source/api.rst>`_
- `Guide with anchor <docs/guide.rst#section>`_

Links that should NOT be rewritten:

- `External <https://example.com>`_
- `Python file <scripts/build.py>`_

.. toctree::

    guide
    tutorial
    api
"""
        )

        (source_dir / "guide.rst").write_text(
            """\
Guide
=====

Section
-------

This is the guide document.
"""
        )

        (source_dir / "tutorial.rst").write_text(
            """\
Tutorial
========

This is the tutorial.
"""
        )

        (source_dir / "api.rst").write_text(
            """\
API Reference
=============

This is the API reference.
"""
        )

        # Build documentation
        build_args = [
            "-b",
            "html",
            "-q",  # quiet
            str(source_dir),
            str(build_dir),
        ]

        result = build_main(build_args)
        assert result == 0, "Sphinx build should succeed"

        # Verify the HTML output
        index_html = (build_dir / "index.html").read_text()

        # Internal links should be rewritten
        assert 'href="guide.html"' in index_html
        assert 'href="tutorial.html"' in index_html
        assert 'href="api.html"' in index_html
        assert 'href="guide.html#section"' in index_html

        # External links and non-matching files should be unchanged
        assert 'href="https://example.com"' in index_html
        assert 'href="scripts/build.py"' in index_html

        # Original .rst links should not appear in HTML
        assert "docs/guide.rst" not in index_html
        assert "./tutorial.rst" not in index_html
        assert "source/api.rst" not in index_html

    def test_custom_configuration_integration(self, tmp_path: Path) -> None:
        """Test with custom configuration settings."""
        build_main = pytest.importorskip("sphinx.cmd.build").build_main

        source_dir = tmp_path / "source"
        build_dir = tmp_path / "build"
        source_dir.mkdir()
        build_dir.mkdir()

        # Custom configuration
        (source_dir / "conf.py").write_text(
            """\
extensions = ['sphinx_linkfix']
sphinx_linkfix_strip_prefixes = ('custom/', 'special/')
sphinx_linkfix_extensions = ('.rst', '.mydoc')
project = 'Custom Test'
master_doc = 'index'
html_theme = 'basic'
"""
        )

        (source_dir / "index.rst").write_text(
            """\
Custom Configuration Test
=========================

- `Custom <custom/doc.rst>`_
- `Special <special/doc.mydoc>`_
- `Unchanged <docs/doc.rst>`_

.. toctree::

    doc
"""
        )

        (source_dir / "doc.rst").write_text(
            """\
Document
========

Test document.
"""
        )

        (source_dir / "doc.mydoc").write_text(
            """\
Special Document
================

Custom extension document.
"""
        )

        build_args = ["-b", "html", "-q", str(source_dir), str(build_dir)]
        result = build_main(build_args)
        assert result == 0

        index_html = (build_dir / "index.html").read_text()

        # Custom prefixes should be stripped
        assert 'href="doc.html"' in index_html

        # Non-matching prefix should remain but be converted to .html
        assert 'href="docs/doc.html"' in index_html

    def test_empty_configuration_integration(self, tmp_path: Path) -> None:
        """Test with empty/default configuration."""
        build_main = pytest.importorskip("sphinx.cmd.build").build_main

        source_dir = tmp_path / "source"
        build_dir = tmp_path / "build"
        source_dir.mkdir()
        build_dir.mkdir()

        # Minimal configuration - extension will use defaults
        (source_dir / "conf.py").write_text(
            """\
extensions = ['sphinx_linkfix']
project = 'Default Test'
master_doc = 'index'
html_theme = 'basic'
"""
        )

        (source_dir / "index.rst").write_text(
            """\
Default Configuration Test
==========================

Using default settings:

- `Docs link <docs/page.rst>`_
- `Source link <source/page.rst>`_
- `Current dir <./page.rst>`_

.. toctree::

    page
"""
        )

        (source_dir / "page.rst").write_text(
            """\
Page
====

Test page.
"""
        )

        build_args = ["-b", "html", "-q", str(source_dir), str(build_dir)]
        result = build_main(build_args)
        assert result == 0

        index_html = (build_dir / "index.html").read_text()

        # Default prefixes should be stripped
        assert 'href="page.html"' in index_html

        # Original links should not be in HTML
        assert "docs/page.rst" not in index_html
        assert "source/page.rst" not in index_html
        assert "./page.rst" not in index_html

    def test_longest_prefix_matching_integration(self, tmp_path: Path) -> None:
        """Test that the longest matching prefix is used in real Sphinx builds."""
        build_main = pytest.importorskip("sphinx.cmd.build").build_main

        source_dir = tmp_path / "source"
        build_dir = tmp_path / "build"
        source_dir.mkdir()
        build_dir.mkdir()

        # Configuration with nested prefixes where longest should win
        (source_dir / "conf.py").write_text(
            """\
extensions = ['sphinx_linkfix']
sphinx_linkfix_strip_prefixes = ('docs/', 'docs/api/', 'docs/api/v1/')
sphinx_linkfix_extensions = ('.rst',)
project = 'Longest Match Test'
master_doc = 'index'
html_theme = 'basic'
"""
        )

        (source_dir / "index.rst").write_text(
            """\
Longest Prefix Match Test
=========================

These links should use the longest matching prefix:

- `API V1 Endpoint <docs/api/v1/endpoint.rst>`_
- `API Guide <docs/api/guide.rst>`_
- `General Docs <docs/readme.rst>`_

.. toctree::

    endpoint
    guide
    readme
"""
        )

        # Create the referenced files
        (source_dir / "endpoint.rst").write_text(
            "API V1 Endpoint\n===============\n\nEndpoint docs."
        )
        (source_dir / "guide.rst").write_text("API Guide\n==========\n\nAPI guide docs.")
        (source_dir / "readme.rst").write_text(
            "General Docs\n============\n\nGeneral documentation."
        )

        build_args = ["-b", "html", "-q", str(source_dir), str(build_dir)]
        result = build_main(build_args)
        assert result == 0

        index_html = (build_dir / "index.html").read_text()

        # Verify that longest prefixes were used:
        # "docs/api/v1/endpoint.rst" should become "endpoint.html" (using "docs/api/v1/")
        assert 'href="endpoint.html"' in index_html
        # "docs/api/guide.rst" should become "guide.html" (using "docs/api/")
        assert 'href="guide.html"' in index_html
        # "docs/readme.rst" should become "readme.html" (using "docs/")
        assert 'href="readme.html"' in index_html

        # Original .rst links should not appear
        assert "docs/api/v1/endpoint.rst" not in index_html
        assert "docs/api/guide.rst" not in index_html
        assert "docs/readme.rst" not in index_html
