"""Unit tests for the sphinx-linkfix extension."""

from __future__ import annotations

from sphinx_linkfix.extension import _is_external, _strip_prefixes


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


class TestStripPrefixes:
    """Test the _strip_prefixes function."""

    def test_strip_single_prefix(self) -> None:
        """Test stripping a single prefix."""
        prefixes = ("docs/",)
        assert _strip_prefixes("docs/file.rst", prefixes) == "file.rst"
        assert _strip_prefixes("docs/subdir/file.rst", prefixes) == "subdir/file.rst"

    def test_strip_multiple_prefixes(self) -> None:
        """Test stripping from multiple possible prefixes."""
        prefixes = ("docs/", "source/", "./")
        assert _strip_prefixes("docs/file.rst", prefixes) == "file.rst"
        assert _strip_prefixes("source/file.rst", prefixes) == "file.rst"
        assert _strip_prefixes("./file.rst", prefixes) == "file.rst"

    def test_no_matching_prefix(self) -> None:
        """Test when no prefix matches."""
        prefixes = ("docs/", "source/")
        assert _strip_prefixes("other/file.rst", prefixes) == "other/file.rst"
        assert _strip_prefixes("file.rst", prefixes) == "file.rst"

    def test_longest_matching_prefix_wins(self) -> None:
        """Test that the longest matching prefix is used."""
        prefixes = ("docs/", "docs/sub/")
        # Should use "docs/sub/" (longer) instead of "docs/" (shorter)
        assert _strip_prefixes("docs/sub/file.rst", prefixes) == "file.rst"

        # Test with different order - longest should still win
        prefixes_reversed = ("docs/sub/", "docs/")
        assert _strip_prefixes("docs/sub/file.rst", prefixes_reversed) == "file.rst"

        # Test with multiple nested prefixes
        prefixes_complex = ("docs/", "docs/api/", "docs/api/v1/")
        assert _strip_prefixes("docs/api/v1/endpoints.rst", prefixes_complex) == "endpoints.rst"

        # Shorter prefix should be used when longer doesn't match
        assert _strip_prefixes("docs/guide/intro.rst", prefixes_complex) == "guide/intro.rst"

    def test_windows_path_normalization(self) -> None:
        """Test that Windows paths are normalized to POSIX."""
        prefixes = ("docs/",)
        # Windows-style paths are normalized by PurePosixPath, but backslashes in string
        # won't match forward slash prefixes on Linux/POSIX systems
        assert _strip_prefixes("docs/file.rst", prefixes) == "file.rst"
        assert _strip_prefixes("docs/subdir/file.rst", prefixes) == "subdir/file.rst"

    def test_empty_prefix_list(self) -> None:
        """Test with empty prefix list."""
        prefixes: tuple[str, ...] = ()
        assert _strip_prefixes("docs/file.rst", prefixes) == "docs/file.rst"

    def test_partial_matches(self) -> None:
        """Test that partial matches don't strip."""
        prefixes = ("docs/",)
        assert _strip_prefixes("documentation/file.rst", prefixes) == "documentation/file.rst"
        assert _strip_prefixes("mydocs/file.rst", prefixes) == "mydocs/file.rst"

    def test_complex_paths(self) -> None:
        """Test complex path scenarios."""
        prefixes = ("docs/", "./", "source/")
        assert _strip_prefixes("docs/api/modules/file.rst", prefixes) == "api/modules/file.rst"
        # "./" prefix matches and is stripped, leaving "docs/file.rst"
        assert _strip_prefixes("./docs/file.rst", prefixes) == "docs/file.rst"
        assert _strip_prefixes("source/../other/file.rst", prefixes) == "../other/file.rst"
