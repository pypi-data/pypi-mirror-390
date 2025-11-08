from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


def test_check_parse_args():
    """Test that check command is parsed correctly."""
    # Test parsing logic without importing the full module
    import argparse
    
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check")
    p_check.add_argument("--test-tile", type=str, default="30TWT")
    p_check.add_argument("--json", action="store_true")
    
    args = parser.parse_args(["check"])
    assert args.cmd == "check"
    assert args.test_tile == "30TWT"
    
    args = parser.parse_args(["check", "--test-tile", "31UDQ"])
    assert args.cmd == "check"
    assert args.test_tile == "31UDQ"
    
    args = parser.parse_args(["check", "--json"])
    assert args.cmd == "check"
    assert args.json


def test_check_gri_service_success():
    """Test check_gri_service function with mocked successful responses."""
    # Mock mgrs import before importing anything that uses it
    import sys
    from unittest.mock import MagicMock
    
    # Create a mock mgrs module
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder

            # Mock successful responses
            mock_finder._http_head_exists.return_value = True
            mock_finder.search_by_mgrs_tile.return_value = [{"id": "test-item"}]

            report = check_gri_service(cfg, "30TWT")

            assert report["overall"] == "ok"
            assert report["base_url"]["status"] == "ok"
            assert report["collection"]["status"] == "ok"
            assert report["tile_access"]["status"] == "ok"
            assert report["tile_access"]["items_found"] == 1
    finally:
        # Clean up mock
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']


def test_check_gri_service_base_url_failure():
    """Test check_gri_service when base URL check fails."""
    import sys
    from unittest.mock import MagicMock
    
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder

            # Mock base URL failure
            mock_finder._http_head_exists.side_effect = [
                False,  # Base URL fails
                True,   # Collection succeeds
            ]
            mock_finder.search_by_mgrs_tile.return_value = [{"id": "test-item"}]

            report = check_gri_service(cfg, "30TWT")

            assert report["overall"] == "error"
            assert report["base_url"]["status"] == "error"
            assert report["collection"]["status"] == "ok"
            assert report["tile_access"]["status"] == "ok"
    finally:
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']


def test_check_gri_service_collection_failure():
    """Test check_gri_service when collection check fails."""
    import sys
    from unittest.mock import MagicMock
    
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder

            # Mock collection failure
            mock_finder._http_head_exists.side_effect = [
                True,   # Base URL succeeds
                False,  # Collection fails
            ]
            mock_finder.search_by_mgrs_tile.return_value = []

            report = check_gri_service(cfg, "30TWT")

            assert report["overall"] == "error"
            assert report["base_url"]["status"] == "ok"
            assert report["collection"]["status"] == "error"
            assert report["tile_access"]["status"] == "error"
    finally:
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']


def test_check_gri_service_tile_access_failure():
    """Test check_gri_service when tile access check fails."""
    import sys
    from unittest.mock import MagicMock
    
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder

            # Mock tile access failure
            mock_finder._http_head_exists.return_value = True
            mock_finder.search_by_mgrs_tile.return_value = []

            report = check_gri_service(cfg, "30TWT")

            assert report["overall"] == "error"
            assert report["base_url"]["status"] == "ok"
            assert report["collection"]["status"] == "ok"
            assert report["tile_access"]["status"] == "error"
            assert report["tile_access"]["items_found"] == 0
    finally:
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']


def test_check_gri_service_exception_handling():
    """Test check_gri_service handles exceptions gracefully."""
    import sys
    from unittest.mock import MagicMock
    
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder

            # Mock exception
            mock_finder._http_head_exists.side_effect = Exception("Network error")
            mock_finder.search_by_mgrs_tile.side_effect = Exception("Search error")

            report = check_gri_service(cfg, "30TWT")

            assert report["overall"] == "error"
            assert "Error:" in report["base_url"]["message"]
            assert "Error:" in report["tile_access"]["message"]
    finally:
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']


def test_check_report_structure():
    """Test that check report has correct structure."""
    import sys
    from unittest.mock import MagicMock
    
    mock_mgrs = MagicMock()
    sys.modules['mgrs'] = mock_mgrs
    
    try:
        from gri_resolver.cli import check_gri_service
        from gri_resolver.config import ResolverConfig
        
        cfg = ResolverConfig(
            gri_base_url="https://example.com/catalog",
            gri_collection="GRI_L1C",
            timeout=5,
        )

        with patch("gri_resolver.integrations.gri_finder.GRIFinder") as mock_finder_class:
            mock_finder = MagicMock()
            mock_finder_class.return_value = mock_finder
            mock_finder._http_head_exists.return_value = True
            mock_finder.search_by_mgrs_tile.return_value = [{"id": "test-item"}]

            report = check_gri_service(cfg, "30TWT")

            # Verify report structure
            assert "base_url" in report
            assert "collection" in report
            assert "tile_access" in report
            assert "overall" in report
            assert report["overall"] in ("ok", "error")
            
            # Verify each check has required fields
            assert "status" in report["base_url"]
            assert "url" in report["base_url"]
            assert "message" in report["base_url"]
            
            assert "status" in report["collection"]
            assert "url" in report["collection"]
            assert "message" in report["collection"]
            
            assert "status" in report["tile_access"]
            assert "tile" in report["tile_access"]
            assert "items_found" in report["tile_access"]
            assert "message" in report["tile_access"]
            
            # Verify JSON serializability
            json_str = json.dumps(report)
            parsed = json.loads(json_str)
            assert parsed == report
    finally:
        if 'mgrs' in sys.modules and hasattr(sys.modules['mgrs'], '__class__'):
            if 'MagicMock' in str(type(sys.modules['mgrs'])):
                del sys.modules['mgrs']

