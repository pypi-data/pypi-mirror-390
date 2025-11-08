from __future__ import annotations

from typing import Iterable, List

from .integrations.stac_mgrs import STACMGRS


def list_tiles_for_roi(bounds: Iterable[float], sample_points: int = 500) -> List[str]:
    return STACMGRS().get_mgrs_tiles_from_roi(list(bounds), sample_points)
