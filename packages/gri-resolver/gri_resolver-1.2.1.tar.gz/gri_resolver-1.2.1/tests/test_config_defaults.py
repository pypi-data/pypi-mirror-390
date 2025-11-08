import sys
from unittest.mock import MagicMock

# Mock mgrs before importing anything that uses it
sys.modules['mgrs'] = MagicMock()

from gri_resolver.config import ResolverConfig


def test_defaults():
    cfg = ResolverConfig()
    assert cfg.cache_ttl_hours == 168
    assert "gri_resolver" in str(cfg.cache_dir)
    assert "gri_resolver" in str(cfg.output_dir)


def test_all_config_parameters():
    """Test that all configuration parameters have default values."""
    cfg = ResolverConfig()
    assert isinstance(cfg.gri_base_url, str)
    assert isinstance(cfg.gri_collection, str)
    assert isinstance(cfg.cache_dir, type(cfg.cache_dir))
    assert isinstance(cfg.output_dir, type(cfg.output_dir))
    assert isinstance(cfg.timeout, int)
    assert isinstance(cfg.cache_ttl_hours, int)
    assert isinstance(cfg.max_workers, int)
    assert isinstance(cfg.force, bool)
    assert isinstance(cfg.quality_selection_enabled, bool)
    assert isinstance(cfg.keep_multiple_per_tile, bool)
    assert isinstance(cfg.prefer_recent, bool)
