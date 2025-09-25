"""Sphinx extension to rewrite internal links in reStructuredText files."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from docutils import nodes
from sphinx.transforms import SphinxTransform
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


class RstLinkRewriter(SphinxTransform):
    """Transform to rewrite internal links in reStructuredText files."""

    default_priority = 210
    supported_builders: tuple[str, ...] = (
        "html",
        "dirhtml",
        "singlehtml",
        "epub",
        "latex",
        "latexpdf",
    )

    def _sanitize_fragment_for_latex(self, fragment: str) -> str:
        """
        Sanitize a fragment for LaTeX compatibility.

        Parameters
        ----------
        fragment: str
            The fragment to sanitize.

        Returns
        -------
        str
            The sanitized fragment.
        """
        if not fragment:
            return ""

        # LaTeX labels should be alphanumeric with hyphens/underscores
        # Convert problematic characters to valid LaTeX label format
        safe_frag = fragment.replace(".", "-").replace(" ", "-")
        return "".join(c for c in safe_frag if c.isalnum() or c in "-_")

    def _process_references(self, prefixes: tuple[str, ...], exts: tuple[str, ...]) -> int:
        """Process and rewrite reference nodes."""
        builder = self.app.builder
        is_latex = builder.name in ("latex", "latexpdf")
        changed = 0

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
            try:
                new_uri = builder.get_target_uri(target_doc)

                # Handle fragments based on builder type
                if frag:
                    if is_latex:
                        frag = self._sanitize_fragment_for_latex(frag)

                    new_uri = f"{new_uri}#{frag}"

                ref["refuri"] = new_uri
                changed += 1
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "[link_rewriter] %s: failed to resolve URI for %s: %s",
                    self.env.docname,
                    target_doc,
                    e,
                )
        return changed

    def _process_images(self, prefixes: tuple[str, ...]) -> int:
        """Process and rewrite image nodes."""
        changed = 0
        for img in list(self.document.traverse(nodes.image)):
            uri = img.get("uri")
            if not uri or _is_external(uri):
                continue

            # Strip prefixes from image paths
            original_uri = uri
            stripped_uri = _strip_prefixes(uri, prefixes)

            if stripped_uri != original_uri:
                img["uri"] = stripped_uri
                changed += 1
        return changed

    def apply(self) -> None:
        """Rewrite internal links in the document."""
        builder = self.app.builder

        # Check if the current builder is supported
        if builder.name not in self.supported_builders:
            logger.debug(
                "[link_rewriter] %s: skipping transformation for unsupported builder '%s'",
                self.env.docname,
                builder.name,
            )
            return

        prefixes = tuple(
            self.app.config.sphinx_linkfix_strip_prefixes or ("docs/", "./", "source/")
        )
        # Extensions to rewrite
        exts = tuple(self.app.config.sphinx_linkfix_extensions or (".rst", ".md", ".txt"))

        # Process references
        changed = self._process_references(prefixes, exts)

        # Process images
        image_changed = self._process_images(prefixes)

        if changed:
            logger.info("[link_rewriter] %s: rewrote %d link(s)", self.env.docname, changed)
        if image_changed:
            logger.info(
                "[link_rewriter] %s: rewrote %d image path(s)",
                self.env.docname,
                image_changed,
            )


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
    app.add_transform(RstLinkRewriter)
    return {"version": "1.0", "parallel_read_safe": True}
