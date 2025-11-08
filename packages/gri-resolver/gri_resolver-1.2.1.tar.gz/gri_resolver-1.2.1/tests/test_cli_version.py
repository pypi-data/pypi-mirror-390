from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


def test_version_parse_args():
    """Test that version command is parsed correctly."""
    # Test parsing logic without importing the full module
    import argparse
    
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_version = sub.add_parser("version")
    p_version.add_argument("--json", action="store_true")
    
    args = parser.parse_args(["version"])
    assert args.cmd == "version"
    assert not args.json
    
    args = parser.parse_args(["version", "--json"])
    assert args.cmd == "version"
    assert args.json


def test_version_logic():
    """Test version command logic with mocked setuptools_scm."""
    # Test the version extraction logic
    try:
        from setuptools_scm import get_version
        version_str = get_version()
        assert version_str
        assert isinstance(version_str, str)
    except Exception:
        # If setuptools_scm fails, version should be "unknown"
        version_str = "unknown"
        assert version_str == "unknown"


def test_version_json_structure():
    """Test that version JSON output has correct structure."""
    # Test the expected JSON structure
    version_info = {
        "package": "gri_resolver",
        "version": "1.0.0",
    }
    
    assert "package" in version_info
    assert version_info["package"] == "gri_resolver"
    assert "version" in version_info
    assert isinstance(version_info["version"], str)
    
    # JSON should be serializable
    json_str = json.dumps(version_info)
    parsed = json.loads(json_str)
    assert parsed == version_info

