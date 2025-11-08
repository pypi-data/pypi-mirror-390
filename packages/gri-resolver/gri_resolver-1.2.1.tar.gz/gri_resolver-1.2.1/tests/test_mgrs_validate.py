import sys
from unittest.mock import MagicMock

# Mock mgrs before importing anything that uses it
mock_mgrs = MagicMock()
# Mock the MGRS class and its methods
mock_mgrs.MGRS = MagicMock()
sys.modules['mgrs'] = mock_mgrs

from gri_resolver.integrations.stac_mgrs import STACMGRS


def test_validate_mgrs():
    m = STACMGRS()
    assert m.validate_utm_gzd("31UDQ") is True
    assert m.validate_utm_gzd("99ZZZ") is False
