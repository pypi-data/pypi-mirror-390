import sys
from unittest.mock import MagicMock

# Mock mgrs before importing anything that uses it
sys.modules['mgrs'] = MagicMock()

from gri_resolver.regions import get_region_bounds


def test_region_bounds_gabon():
    b = get_region_bounds("gabon")
    assert isinstance(b, list)
    assert len(b) == 4
