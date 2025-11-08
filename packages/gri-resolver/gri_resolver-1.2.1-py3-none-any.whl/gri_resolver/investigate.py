from __future__ import annotations

from typing import Any, Dict, List, Optional

from .logging import get_logger
from .integrations.gri_finder import GRIFinder
from .config import ResolverConfig


class Investigator:
    def __init__(self, config: Optional[ResolverConfig] = None, log_level: str = "INFO"):
        self.config = config or ResolverConfig()
        self.logger = get_logger(__name__, log_level)
        self._finder = GRIFinder({
            "catalog_url": self.config.gri_base_url,
            "collection": self.config.gri_collection,
            "timeout": self.config.timeout,
        }, self.logger)

    def check_presence_for_tiles(self, tiles: List[str]) -> Dict[str, bool]:
        presence: Dict[str, bool] = {}
        for t in tiles:
            try:
                presence[t] = len(self._finder.search_by_mgrs_tile(t, limit=1)) > 0
            except Exception:
                presence[t] = False
        return presence

    def inspect_items_for_tiles(
        self,
        tiles: List[str],
        limit_per_tile: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        out: Dict[str, List[Dict[str, Any]]] = {}
        for t in tiles:
            items = self._finder.search_by_mgrs_tile(t)
            if limit_per_tile is not None:
                items = items[:limit_per_tile]
            out[t] = items
        return out
