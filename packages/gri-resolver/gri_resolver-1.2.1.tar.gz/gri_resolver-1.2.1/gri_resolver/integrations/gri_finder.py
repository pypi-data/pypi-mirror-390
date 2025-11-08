from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import requests

from .stac_mgrs import STACMGRS


class GRIFinder:
    """GRI tile-based finder independent of gcp_creator.

    Implements minimal static STAC traversal using MGRS tile paths to avoid
    catalog-wide scans. Expects a static catalog layout under gri_base_url.
    """

    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self._mgrs = STACMGRS()
        self._base = (self.config.get("catalog_url") or "").rstrip("/")
        self._timeout = int(self.config.get("timeout", 60))
        self._collection = (self.config.get("collection") or "").strip("/")
        self._deep_scan = bool(self.config.get("deep_scan", False))

    def _http_get_json(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(url, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            self.logger.debug(f"GET {url} failed: {exc}")
            return None

    def _http_head_exists(self, url: str) -> bool:
        try:
            resp = requests.head(url, timeout=self._timeout)
            return 200 <= resp.status_code < 300
        except Exception:
            return False

    def _collect_item_links(self, catalog: Dict[str, Any]) -> List[str]:
        links = catalog.get("links", []) or []
        return [link.get("href") for link in links if link.get("rel") in ("item", "items")]  # some catalogs use items

    def _collect_child_catalogs(self, catalog: Dict[str, Any]) -> List[str]:
        links = catalog.get("links", []) or []
        return [link.get("href") for link in links if link.get("rel") in ("child", "collection")]

    def _normalize_url(self, href: str, parent: str) -> str:
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if href.startswith("/"):
            # absolute path on same host is not supported; join naively
            return f"{self._base}{href}"
        # relative
        if parent.endswith("/"):
            return parent + href
        # strip filename
        idx = parent.rfind("/")
        base_dir = parent[: idx + 1] if idx >= 0 else parent + "/"
        return base_dir + href

    def _fetch_items_from_catalog_tree(self, root_url: str, limit: Optional[int]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        to_visit: List[str] = [root_url]
        seen = set()
        while to_visit:
            url = to_visit.pop()
            if url in seen:
                continue
            seen.add(url)
            cat = self._http_get_json(url)
            if not cat:
                continue
            # If this is directly an item, return it
            if cat.get("type") == "Feature" and cat.get("id"):
                items.append(cat)
                return items if limit is None else items[:limit]
            # gather direct item links
            for href in self._collect_item_links(cat):
                item_url = self._normalize_url(href, url)
                item = self._http_get_json(item_url)
                if item and item.get("type") == "Feature":
                    items.append(item)
                    if limit is not None and len(items) >= limit:
                        return items
            # traverse children
            for href in self._collect_child_catalogs(cat):
                child = self._normalize_url(href, url)
                to_visit.append(child)
        return items

    def search_by_mgrs_tile(self, tile: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self._base:
            self.logger.warning("catalog_url is not configured; returning 0 items")
            return []
        if not self._mgrs.validate_utm_gzd(tile):
            self.logger.warning(f"Invalid MGRS tile: {tile}")
            return []
        variants = self._mgrs.construct_utm_gzd_path_variants(tile)
        items: List[Dict[str, Any]] = []
        seen_item_ids = set()
        # Fast path: try direct *_item.json with HEAD, then GET all found items
        for tile_path in variants:
            direct_candidates = []
            if self._collection:
                direct_candidates.append(f"{self._base}/{self._collection}/{tile_path}_item.json")
            direct_candidates.append(f"{self._base}/{tile_path}_item.json")
            for url in direct_candidates:
                if self._http_head_exists(url):
                    item = self._http_get_json(url)
                    if item and item.get("type") == "Feature":
                        item_id = item.get("id")
                        if item_id and item_id not in seen_item_ids:
                            items.append(item)
                            seen_item_ids.add(item_id)
        # If we found items and deep scan is disabled, return what we have
        if items and not self._deep_scan:
            if limit is not None and len(items) > limit:
                return items[:limit]
            return items
        # Optional deep scan to find additional items
        for tile_path in variants:
            roots = []
            if self._collection:
                roots.append(f"{self._base}/{self._collection}/{tile_path}/catalog.json")
            roots.append(f"{self._base}/{tile_path}/catalog.json")
            for root in roots:
                self.logger.debug(f"Trying tile catalog: {root}")
                got = self._fetch_items_from_catalog_tree(root, None)  # Get all, filter by seen_ids
                if got:
                    for item in got:
                        item_id = item.get("id")
                        if item_id and item_id not in seen_item_ids:
                            items.append(item)
                            seen_item_ids.add(item_id)
                            if limit is not None and len(items) >= limit:
                                return items[:limit]
        return items

    def convert_stac_item_to_reference(
        self,
        item: Dict[str, Any],
        target_bounds: Tuple[float, float, float, float],
        target_crs: str = "EPSG:32632",
    ) -> Optional[Dict[str, Any]]:
        _ = (target_bounds, target_crs)
        return {"stac_item": item}

    def download_reference_image(self, reference_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # the outer resolver handles download via downloader module
        return None
