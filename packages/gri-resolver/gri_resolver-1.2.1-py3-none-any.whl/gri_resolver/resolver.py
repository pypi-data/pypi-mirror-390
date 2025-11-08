from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import ResolverConfig
from .logging import get_logger
from .tiles import list_tiles_for_roi
from .integrations.gri_finder import GRIFinder
from .downloader import handle_reference_download
from .cache import CacheIndex
from .regions import get_region_bounds
from .item_scoring import extract_quality_metadata, score_item_quality


@dataclass
class ResolveResult:
    region_name: Optional[str]
    bounds: Optional[Tuple[float, float, float, float]]
    mgrs_tiles: List[str]
    gri_items: List[Dict[str, Any]]
    unresolved_tiles: List[str]
    downloaded_files: List[str]
    failed_files: List[str]
    downloaded_items: int
    failed_items: int
    download_dir: str
    cache_dir: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GRIResolver:
    def __init__(
        self,
        config: Optional[ResolverConfig] = None,
        log_level: str = "INFO",
    ):
        self.config = config or ResolverConfig()
        self.config.ensure_dirs()
        self.logger = get_logger(__name__, log_level)
        self._finder = GRIFinder({
            "catalog_url": self.config.gri_base_url,
            "collection": self.config.gri_collection,
            "cache_dir": str(self.config.cache_dir),
            "output_dir": str(self.config.output_dir),
            "timeout": self.config.timeout,
            "cache_ttl_hours": self.config.cache_ttl_hours,
        }, self.logger)
        self._cache = CacheIndex(self.config.cache_dir)

    def resolve_tiles(
        self,
        tiles: List[str],
        *,
        limit: Optional[int] = None,
        force: bool = False,
        progress_cb: Optional[callable] = None,
        progress_update_cb: Optional[callable] = None,
        use_tqdm: bool = False,
    ) -> ResolveResult:
        all_items: List[Dict[str, Any]] = []
        unresolved: List[str] = []
        single_tile = len(tiles) == 1
        tiles_bar = None
        # maybe_emit will print status lines only when no tqdm bar is used
        # (to avoid mixing bar output with text). For a single tile, we already
        # suppress most messages elsewhere.

        def maybe_emit(msg: str) -> None:
            # Suppress text messages when tqdm is enabled to avoid mixing output
            # Only emit text when progress_cb is provided AND tqdm is not active
            # Web mode (progress_update_cb is not None) should always receive messages via progress_cb
            if progress_cb is not None:
                # Always emit in web mode (when progress_update_cb is provided)
                # In CLI mode, only emit if tqdm is not enabled
                if progress_update_cb is not None or not use_tqdm:
                    progress_cb(msg)
        # Optional user-friendly progress using tqdm when available and requested
        # Use tqdm only when explicitly requested (use_tqdm=True) and not in web mode
        # Web mode is detected by progress_update_cb being set
        tiles_iter = tiles
        tiles_bar = None
        if not single_tile:
            # Use tqdm only if explicitly requested and not in web mode
            if progress_update_cb is None and use_tqdm:  # CLI mode with --progress
                try:
                    from tqdm import tqdm  # type: ignore
                    tiles_bar = tqdm(total=len(tiles), desc="Tiles", unit="tile")
                except Exception:
                    tiles_bar = None
            # else: web mode or no --progress, don't use tqdm (tiles_bar stays None)

        # Collect items by tile, then select best per tile if quality selection is enabled
        items_by_tile: Dict[str, List[Dict[str, Any]]] = {}
        for tile in tiles_iter:
            try:
                maybe_emit(f"searching tile {tile}...")
                items = self._finder.search_by_mgrs_tile(tile, limit=None)  # Get all items for selection
                if not items:
                    unresolved.append(tile)
                    maybe_emit(f"tile {tile}: 0 items")
                else:
                    items_by_tile[tile] = items
                    maybe_emit(f"tile {tile}: {len(items)} items")
            except Exception as exc:
                self.logger.error(f"Tile {tile} error: {exc}")
                unresolved.append(tile)
            finally:
                if tiles_bar is not None:
                    try:
                        tiles_bar.set_description(f"Tile {tile}")
                    except Exception:
                        pass
                    tiles_bar.update(1)
                elif progress_cb:
                    # When using web callback, update progress via callback instead of tqdm
                    pass  # Progress already sent via maybe_emit

        # Select best item per tile if quality selection is enabled
        if self.config.quality_selection_enabled:
            for tile, items in items_by_tile.items():
                if len(items) > 1:
                    # Score all items and select the best
                    scored_items = []
                    for item in items:
                        metadata = extract_quality_metadata(item)
                        score = score_item_quality(item, metadata, self.config.prefer_recent)
                        scored_items.append((score, item, metadata))
                    # Sort by score (descending) and take the best
                    scored_items.sort(key=lambda x: x[0], reverse=True)
                    best_score, best_item, best_metadata = scored_items[0]
                    items_by_tile[tile] = [best_item]
                    maybe_emit(f"tile {tile}: selected best item (score={best_score:.2f})")
                elif len(items) == 1:
                    # Single item, still extract metadata for caching
                    item = items[0]
                    metadata = extract_quality_metadata(item)
                    score = score_item_quality(item, metadata, self.config.prefer_recent)
                    # Store metadata in item for later use
                    item["_quality_metadata"] = metadata
                    item["_quality_score"] = score

        # Flatten items_by_tile back to all_items list
        all_items = []
        for tile, items in items_by_tile.items():
            all_items.extend(items)

        # Keep a global limit as a guard if provided
        if limit is not None and len(all_items) > limit:
            all_items = all_items[:limit]

        downloaded_files: List[str] = []
        failed_files: List[str] = []
        downloaded_items = 0
        failed_items = 0

        # Parallel or serial download phase
        from concurrent.futures import ThreadPoolExecutor, as_completed
        workers = max(1, int(self.config.max_workers))
        use_parallel = workers > 1 and len(all_items) > 1
        items_bar = None
        bytes_bar = None
        active_items = set()
        active_lock = None
        # Use tqdm only when explicitly requested (use_tqdm=True) and not in web mode
        # Web mode is detected by progress_update_cb being set
        if use_parallel:
            if progress_update_cb is None and use_tqdm:  # CLI mode with --progress
                try:
                    from tqdm import tqdm  # type: ignore
                    import threading
                    items_bar = tqdm(total=len(all_items), desc="Items", unit="it", leave=False)
                    # Global bytes bar (unknown total): shows cumulative bytes downloaded
                    bytes_bar = tqdm(total=0, desc="Bytes", unit="B", unit_scale=True, unit_divisor=1024, leave=True)
                    active_lock = threading.Lock()
                except Exception:
                    items_bar = None
                    bytes_bar = None
                    active_lock = None
            # else: web mode or no --progress, don't use tqdm (items_bar, bytes_bar stay None)

        def process_item(idx_item: int, item: Dict[str, Any]) -> None:
            nonlocal downloaded_items, failed_items
            item_id = item.get("id", f"item_{idx_item}")
            # Derive a compact tile code (e.g., 33NTB) from item id like GRI_L1C_T33NTB
            tile_code = item_id
            try:
                import re as _re
                m = _re.search(r"_T(\d{2}[A-Z][A-Z]{2})", item_id)
                if m:
                    tile_code = m.group(1)
            except Exception:
                pass
            # Check cache: use get_best_for_tile if quality selection enabled, else get(item_id)
            cached = None
            if self.config.quality_selection_enabled:
                cached = self._cache.get_best_for_tile(tile_code)
            else:
                cached = self._cache.get(item_id)

            if cached and not force:
                downloaded_files.append(str(cached))
                downloaded_items += 1
                maybe_emit(f"cached {item_id}")
                if items_bar is not None:
                    items_bar.update(1)
                return
            try:
                bar = None

                def _progress_update(kind: str, value: int, total: int) -> None:
                    nonlocal bar
                    # If we have a progress_update_cb (web interface), call it for fine-grained updates
                    if progress_update_cb is not None:
                        # Always pass item_id as file_name so the web interface can track it properly
                        file_name = item_id
                        try:
                            progress_update_cb(kind, value, total, file_name)
                        except Exception:
                            pass  # Ignore errors in callback

                    # In parallel mode, aggregate bytes on a global bar
                    if use_parallel:
                        if bytes_bar is not None:
                            if kind == "start":
                                try:
                                    if active_lock is not None:
                                        with active_lock:
                                            active_items.add(tile_code)
                                            preview = ", ".join(list(active_items))
                                            if len(preview) > 60:
                                                preview = preview[:57] + "..."
                                            bytes_bar.set_postfix_str(preview)
                                except Exception:
                                    pass
                            if kind == "bytes":
                                try:
                                    bytes_bar.update(value)
                                    if active_lock is not None:
                                        with active_lock:
                                            preview = ", ".join(list(active_items))
                                            if len(preview) > 60:
                                                preview = preview[:57] + "..."
                                            bytes_bar.set_postfix_str(preview)
                                except Exception:
                                    pass
                        return
                    # Serial mode: per-item bar (only in CLI mode with --progress, not web mode)
                    if progress_update_cb is not None:
                        return  # Web interface, don't use tqdm
                    if not use_tqdm:
                        return  # CLI mode without --progress, don't use tqdm
                    try:
                        from tqdm import tqdm  # type: ignore
                    except Exception:
                        return
                    if kind == "start" and total > 0:
                        bar = tqdm(total=total, desc=f"{tile_code}", unit="B", unit_scale=True, unit_divisor=1024)
                    elif kind == "bytes" and bar is not None:
                        bar.update(value)
                    elif kind == "stage" and bar is not None:
                        try:
                            bar.set_postfix_str("extracting")
                        except Exception:
                            pass
                ref = self._finder.convert_stac_item_to_reference(
                    item=item,
                    target_bounds=(0.0, 0.0, 0.0, 0.0),
                    target_crs="EPSG:32632",
                )
                if not ref:
                    failed_items += 1
                    failed_files.append(item_id)
                    maybe_emit(f"failed reference {item_id}")
                    if items_bar is not None:
                        items_bar.update(1)
                    return
                # For web interface, use progress_cb for messages, but also pass progress_update
                # For CLI, suppress textual progress_cb during bars to avoid noisy overlays
                cb = None if (progress_cb is not None and items_bar is not None) else progress_cb
                dl = handle_reference_download(ref, self.config.output_dir, self.logger, cb, _progress_update)
                if dl and dl.get("paths"):
                    downloaded_items += 1
                    image_paths = dl["paths"]
                    downloaded_files.extend(image_paths)
                    # Extract quality metadata if not already extracted
                    if "_quality_metadata" in item and "_quality_score" in item:
                        metadata = item["_quality_metadata"]
                        score = item["_quality_score"]
                    else:
                        metadata = extract_quality_metadata(item)
                        score = score_item_quality(item, metadata, self.config.prefer_recent)
                    # Store all images in cache with quality metadata
                    # Use item_id as base, append index for multiple images
                    for idx, image_path in enumerate(image_paths):
                        if idx == 0:
                            # First image uses the item_id directly
                            cache_item_id = item_id
                        else:
                            # Additional images use item_id with suffix
                            cache_item_id = f"{item_id}_img{idx}"
                        self._cache.put(
                            cache_item_id,
                            Path(image_path),
                            tile_code=tile_code,
                            quality_score=score,
                            metadata=metadata,
                        )
                    maybe_emit(f"downloaded {item_id} ({len(image_paths)} image(s))")
                else:
                    failed_items += 1
                    failed_files.append(item_id)
                    maybe_emit(f"failed download {item_id}")
            except Exception as exc:
                self.logger.error(f"Download error for {item_id}: {exc}")
                failed_items += 1
                failed_files.append(item_id)
                maybe_emit(f"error {item_id}: {exc}")
            finally:
                try:
                    if 'bar' in locals() and bar is not None:
                        bar.close()
                except Exception:
                    pass
                if items_bar is not None:
                    items_bar.update(1)
                if use_parallel and bytes_bar is not None and active_lock is not None:
                    try:
                        with active_lock:
                            if tile_code in active_items:
                                active_items.remove(tile_code)
                                preview = ", ".join(list(active_items))
                                if len(preview) > 60:
                                    preview = preview[:57] + "..."
                                bytes_bar.set_postfix_str(preview)
                    except Exception:
                        pass

        if use_parallel:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = [ex.submit(process_item, i, it) for i, it in enumerate(all_items, 1)]
                for _ in as_completed(futures):
                    pass
            if items_bar is not None:
                items_bar.close()
            if bytes_bar is not None:
                bytes_bar.close()
        else:
            for idx, item in enumerate(all_items, 1):
                process_item(idx, item)

        return ResolveResult(
            region_name=None,
            bounds=None,
            mgrs_tiles=tiles,
            gri_items=all_items,
            unresolved_tiles=unresolved,
            downloaded_files=downloaded_files,
            failed_files=failed_files,
            downloaded_items=downloaded_items,
            failed_items=failed_items,
            download_dir=str(self.config.output_dir),
            cache_dir=str(self.config.cache_dir),
        )

    def resolve_roi(
        self,
        bounds: Tuple[float, float, float, float],
        *,
        sample_points: int = 500,
        limit: Optional[int] = None,
        force: bool = False,
        progress_cb: Optional[callable] = None,
        progress_update_cb: Optional[callable] = None,
        use_tqdm: bool = False,
    ) -> ResolveResult:
        tiles = list_tiles_for_roi(bounds, sample_points)
        return self.resolve_tiles(
            tiles,
            limit=limit,
            force=force,
            progress_cb=progress_cb,
            progress_update_cb=progress_update_cb,
            use_tqdm=use_tqdm,
        )

    def resolve_region(
        self,
        region: str,
        *,
        sample_points: int = 500,
        limit: Optional[int] = None,
        force: bool = False,
        progress_cb: Optional[callable] = None,
        progress_update_cb: Optional[callable] = None,
        use_tqdm: bool = False,
    ) -> ResolveResult:
        bounds = get_region_bounds(region)
        if not bounds:
            self.logger.error(f"Unknown region: {region}")
            return ResolveResult(
                region_name=region,
                bounds=None,
                mgrs_tiles=[],
                gri_items=[],
                unresolved_tiles=[],
                downloaded_files=[],
                failed_files=[],
                downloaded_items=0,
                failed_items=0,
                download_dir=str(self.config.output_dir),
                cache_dir=str(self.config.cache_dir),
            )
        tiles = list_tiles_for_roi(bounds, sample_points)
        result = self.resolve_tiles(
            tiles,
            limit=limit,
            force=force,
            progress_cb=progress_cb,
            progress_update_cb=progress_update_cb,
            use_tqdm=use_tqdm,
        )
        result.region_name = region
        result.bounds = tuple(bounds)  # type: ignore[assignment]
        return result
