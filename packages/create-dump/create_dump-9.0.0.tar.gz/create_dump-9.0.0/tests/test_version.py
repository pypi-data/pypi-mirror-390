# tests/test_version.py

"""
Tests for src/create_dump/version.py
"""

from create_dump.version import __version__, VERSION


def test_version_consistency():
    """Test Case 1: __version__ and VERSION are identical."""
    assert __version__ == VERSION
    assert __version__ == "9.0.0"  # Pin to current; update on release


def test_version_format_semver():
    """Test Case 2: Version adheres to semantic versioning pattern."""
    import re
    # 🐞 FIX: Update regex to be PEP 440-compliant, allowing for .devN suffixes
    semver_pattern = r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:\.dev\d+)?(?:-(?P<prerelease>[a-zA-Z0-9.-]+))?(?:\+(?P<build>[a-zA-Z0-9.-]+))?$"
    match = re.match(semver_pattern, __version__)
    assert match is not None, f"Version {__version__} does not match semver"
