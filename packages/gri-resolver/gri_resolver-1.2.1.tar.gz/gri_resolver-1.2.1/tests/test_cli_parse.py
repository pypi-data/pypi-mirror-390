import sys
from unittest.mock import MagicMock

# Mock mgrs before importing anything that uses it
sys.modules['mgrs'] = MagicMock()

from gri_resolver.cli import parse_args


def test_parse_tiles_mode():
    ns = parse_args(["resolve", "--tiles", "31UDQ"])
    assert ns.cmd == "resolve"
    assert ns.tiles == ["31UDQ"]


def test_parse_with_cache_ttl_hours():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--cache-ttl-hours", "200"])
    assert ns.cmd == "resolve"
    assert ns.tiles == ["31UDQ"]
    assert ns.cache_ttl_hours == 200


def test_parse_with_quality_selection():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--quality-selection"])
    assert ns.cmd == "resolve"
    assert ns.quality_selection_enabled is True


def test_parse_with_no_quality_selection():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--no-quality-selection"])
    assert ns.cmd == "resolve"
    assert ns.quality_selection_enabled is False


def test_parse_with_prefer_recent():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--prefer-recent"])
    assert ns.cmd == "resolve"
    assert ns.prefer_recent is True


def test_parse_with_keep_multiple_per_tile():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--keep-multiple-per-tile"])
    assert ns.cmd == "resolve"
    assert ns.keep_multiple_per_tile is True


def test_parse_with_no_keep_multiple_per_tile():
    ns = parse_args(["resolve", "--tiles", "31UDQ", "--no-keep-multiple-per-tile"])
    assert ns.cmd == "resolve"
    assert ns.keep_multiple_per_tile is False
