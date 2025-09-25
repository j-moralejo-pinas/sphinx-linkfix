"""Sphinx extension to rewrite internal links in reStructuredText files."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging

logger = logging.getLogger(__name__)


def _is_external(href: str) -> bool:
    """
    Check if a given href is an external link.

    Parameters
    ----------
    href: str
        The URL to check.

    Returns
    -------
    bool
        True if the URL is external, False otherwise.
    """
    parsed = urlparse(href)
    return bool(parsed.scheme and parsed.netloc)


def _strip_prefixes(path_str: str, prefixes: tuple[str, ...]) -> str:
    """
    Remove leading folder prefixes from a path string.

    Parameters
    ----------
    path_str: str
        The path string to modify.
    prefixes: tuple[str, ...]
        A tuple of prefixes to remove.

    Returns
    -------
    str
        The modified path string with the prefixes removed.
    """
    # For prefix matching, we need to work with the original path
    # but ensure cross-platform compatibility
    original_path = path_str.replace("\\", "/")  # Convert backslashes to forward slashes

    # Find the longest matching prefix
    longest_match = ""
    for pref in prefixes:
        normalized_pref = pref.replace("\\", "/")  # Normalize prefix too
        if original_path.startswith(normalized_pref) and len(normalized_pref) > len(longest_match):
            longest_match = normalized_pref

    if longest_match:
        result = original_path[len(longest_match) :]
        # Now normalize the result using PurePosixPath to clean up any .. or . components
        return str(PurePosixPath(result))

    # If no prefix matched, normalize the whole path
    return str(PurePosixPath(original_path))


class RstLinkRewriter(SphinxPostTransform):
    """Post-transform to rewrite internal links in reStructuredText files."""

    default_priority = 999

    def run(self) -> None:
        """Rewrite internal links in the document."""
        builder = self.app.builder
        changed = 0
        prefixes = tuple(
            self.app.config.sphinx_linkfix_strip_prefixes or ("docs/", "./", "source/")
        )
        # Extensions to rewrite
        exts = tuple(self.app.config.sphinx_linkfix_extensions or (".rst", ".md", ".txt"))

        for ref in list(self.document.traverse(nodes.reference)):
            uri = ref.get("refuri")
            if not uri or _is_external(uri):
                continue

            if "#" in uri:
                path_str, frag = uri.split("#", 1)
                frag = frag.strip()
            else:
                path_str, frag = uri, ""

            path = PurePosixPath(path_str)
            if path.suffix not in exts:
                continue

            # Remove leading folder prefixes like "docs/"
            path_str = _strip_prefixes(path_str, prefixes)

            target_doc = str(PurePosixPath(path_str).with_suffix("")).lstrip("./")
            html_uri = builder.get_target_uri(target_doc)
            if frag:
                html_uri = f"{html_uri}#{frag}"

            ref["refuri"] = html_uri
            changed += 1

        if changed:
            logger.info("[link_rewriter] %s: rewrote %d link(s)", self.env.docname, changed)


def setup(app: Any) -> dict[str, str | bool]:
    """
    Set up the Sphinx extension.

    Parameters
    ----------
    app: Any
        The Sphinx application object.

    Returns
    -------
    dict[str, str | bool]
        A dictionary with extension metadata.
    """
    logger.info("[link_rewriter] extension loaded")
    app.add_config_value("sphinx_linkfix_strip_prefixes", (), "env")
    app.add_config_value("sphinx_linkfix_extensions", (), "env")
    app.add_post_transform(RstLinkRewriter)
    return {"version": "1.0", "parallel_read_safe": True}
