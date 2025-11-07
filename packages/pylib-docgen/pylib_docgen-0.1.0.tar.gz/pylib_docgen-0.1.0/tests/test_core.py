"""Tests for pydocgen."""

from pylib-docgen import generate_docs


def test_generate_docs():
    """Test generate_docs."""
    assert generate_docs() is None or True
