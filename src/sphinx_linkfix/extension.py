"""Sphinx extension to rewrite internal links in reStructuredText files."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from docutils import nodes
from sphinx.transforms import SphinxTransform
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


def _strip_docs_prefix(path_str: str, docs_relative_path: str) -> str:
    """
    Remove the leading docs folder prefix from a path string.

    Parameters
    ----------
    path_str: str
        The path string to modify.
    docs_relative_path: str
        The prefix to remove.

    Returns
    -------
    str
        The modified path string with the prefix removed.
    """
    # Use PurePosixPath for cross-platform path normalization
    original_path = PurePosixPath(path_str)
    normalized_prefix = PurePosixPath(docs_relative_path)

    # Convert both to string for prefix matching (PurePosixPath handles normalization)
    original_str = str(original_path)
    prefix_str = str(normalized_prefix)

    if original_str.startswith(prefix_str):
        # Remove the prefix and return the remaining path
        result = original_str[len(prefix_str) :]
        # Strip leading slash if present and normalize
        return str(PurePosixPath(result)).lstrip("/")

    # If no prefix matched, return the normalized path
    return original_str


class RstImageRewriter(SphinxTransform):
    """Transform to rewrite image paths early in the process."""

    default_priority = 210
    supported_builders: tuple[str, ...] = (
        "html",
        "dirhtml",
        "singlehtml",
        "epub",
        "latex",
        "latexpdf",
    )

    def apply(self) -> None:
        """Rewrite image paths in the document."""
        builder = self.app.builder

        # Check if the current builder is supported
        if builder.name not in self.supported_builders:
            return

        docs_relative_path = self.app.config.docs_relative_path or "docs/"

        # Process images only
        changed = 0
        for img in list(self.document.traverse(nodes.image)):
            uri = img.get("uri")
            if not uri or _is_external(uri):
                continue

            # Strip prefix from image paths
            original_uri = uri
            stripped_uri = _strip_docs_prefix(uri, docs_relative_path)

            if stripped_uri != original_uri:
                img["uri"] = stripped_uri
                changed += 1

        if changed:
            logger.info(
                "[link_rewriter] %s: rewrote %d image path(s)",
                self.env.docname,
                changed,
            )


class RstLinkRewriter(SphinxPostTransform):
    """Post-transform to rewrite internal links in reStructuredText files."""

    default_priority = 999
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

    def _process_references(self, docs_relative_path: str, exts: tuple[str, ...]) -> int:
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

            # Remove leading folder prefix
            path_str = _strip_docs_prefix(path_str, docs_relative_path)

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
            except Exception:
                logger.exception(
                    "[link_rewriter] %s: failed to resolve URI for %s",
                    self.env.docname,
                    target_doc,
                )
        return changed

    def run(self) -> None:
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

        docs_relative_path = self.app.config.docs_relative_path or "docs/"
        # Extensions to rewrite
        exts = tuple(self.app.config.sphinx_linkfix_extensions or (".rst", ".md", ".txt"))

        # Process references only (images are handled by RstImageRewriter)
        changed = self._process_references(docs_relative_path, exts)

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
    app.add_config_value("docs_relative_path", "docs/", "env")
    app.add_config_value("sphinx_linkfix_extensions", (), "env")
    app.add_transform(RstImageRewriter)  # Early transform for images
    app.add_post_transform(RstLinkRewriter)  # Late transform for references
    return {"version": "1.0", "parallel_read_safe": True}
