"""Unit tests for the sphinx-linkfix extension."""

from __future__ import annotations

from sphinx_linkfix.extension import _is_external, _strip_docs_prefix


class TestIsExternal:
    """Test the _is_external function."""

    def test_external_https_url(self) -> None:
        """Test that HTTPS URLs are recognized as external."""
        assert _is_external("https://example.com")
        assert _is_external("https://github.com/user/repo")
        assert _is_external("https://docs.python.org/")

    def test_external_http_url(self) -> None:
        """Test that HTTP URLs are recognized as external."""
        assert _is_external("http://example.com")
        assert _is_external("http://localhost:8080")

    def test_external_other_schemes(self) -> None:
        """Test that other URL schemes are recognized as external."""
        assert _is_external("ftp://ftp.example.com")
        # URLs without netloc are not considered external by the implementation
        assert not _is_external("mailto:user@example.com")
        assert not _is_external("file:///path/to/file")

    def test_internal_relative_paths(self) -> None:
        """Test that relative paths are not external."""
        assert not _is_external("../other/file.rst")
        assert not _is_external("./file.rst")
        assert not _is_external("file.rst")
        assert not _is_external("subdir/file.rst")

    def test_internal_absolute_paths(self) -> None:
        """Test that absolute paths are not external."""
        assert not _is_external("/docs/file.rst")
        assert not _is_external("/path/to/file.rst")

    def test_fragments_only(self) -> None:
        """Test that fragment-only links are not external."""
        assert not _is_external("#section")
        assert not _is_external("#some-heading")

    def test_paths_with_fragments(self) -> None:
        """Test paths with fragments."""
        assert not _is_external("file.rst#section")
        assert not _is_external("../other/file.rst#heading")
        assert _is_external("https://example.com#section")

    def test_empty_and_special_cases(self) -> None:
        """Test edge cases."""
        assert not _is_external("")
        assert not _is_external("file with spaces.rst")
        assert not _is_external("file-with-dashes.rst")


class TestStripDocsPrefix:
    """Test the _strip_docs_prefix function."""

    def test_strip_docs_prefix(self) -> None:
        """Test stripping the docs prefix."""
        docs_path = "docs/"
        assert _strip_docs_prefix("docs/file.rst", docs_path) == "file.rst"
        assert _strip_docs_prefix("docs/subdir/file.rst", docs_path) == "subdir/file.rst"

    def test_strip_custom_prefix(self) -> None:
        """Test stripping a custom prefix."""
        docs_path = "source/"
        assert _strip_docs_prefix("source/file.rst", docs_path) == "file.rst"
        assert _strip_docs_prefix("source/subdir/file.rst", docs_path) == "subdir/file.rst"

    def test_no_matching_prefix(self) -> None:
        """Test when prefix doesn't match."""
        docs_path = "docs/"
        assert _strip_docs_prefix("other/file.rst", docs_path) == "other/file.rst"
        assert _strip_docs_prefix("file.rst", docs_path) == "file.rst"

    def test_partial_matches(self) -> None:
        """Test that partial matches don't strip."""
        docs_path = "docs/"
        assert _strip_docs_prefix("documentation/file.rst", docs_path) == "documentation/file.rst"
        assert _strip_docs_prefix("mydocs/file.rst", docs_path) == "mydocs/file.rst"

    def test_windows_path_normalization(self) -> None:
        """Test that Windows paths are normalized to POSIX."""
        docs_path = "docs/"
        assert _strip_docs_prefix("docs/file.rst", docs_path) == "file.rst"
        assert _strip_docs_prefix("docs/subdir/file.rst", docs_path) == "subdir/file.rst"

    def test_complex_paths(self) -> None:
        """Test complex path scenarios."""
        docs_path = "docs/"
        assert _strip_docs_prefix("docs/api/modules/file.rst", docs_path) == "api/modules/file.rst"

    def test_empty_prefix(self) -> None:
        """Test with empty prefix."""
        docs_path = ""
        assert _strip_docs_prefix("docs/file.rst", docs_path) == "docs/file.rst"

    def test_current_directory_prefix(self) -> None:
        """Test with current directory prefix."""
        docs_path = "./"
        assert _strip_docs_prefix("./file.rst", docs_path) == "file.rst"
        assert _strip_docs_prefix("./docs/file.rst", docs_path) == "docs/file.rst"
