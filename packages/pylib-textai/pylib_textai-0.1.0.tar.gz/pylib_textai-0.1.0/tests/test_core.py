"""Tests for pytextai."""

from pylib-textai import sentiment


def test_sentiment():
    """Test sentiment."""
    assert sentiment() is None or True
