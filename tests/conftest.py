"""
Pytest configuration fixtures for sphinx-linkfix tests.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
- https://docs.pytest.org/en/stable/fixture.html
- https://docs.pytest.org/en/stable/writing_plugins.html
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may require Sphinx)"
    )


def pytest_collection_modifyitems(_config: pytest.Config, items: list[pytest.Item]) -> None:
    """Automatically mark integration tests."""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
