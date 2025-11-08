# gri_resolver – Developer Guide (Python API)

This document describes how to use the Python API of `gri_resolver` to:
- Resolve items by MGRS tiles (no full catalog scan)
- Download and extract images from GRI archives
- Inspect/presence-check items without downloading
- Control caching and parallelism

## Quickstart

```python
from gri_resolver import GRIResolver, ResolverConfig

# Configure
cfg = ResolverConfig(
    gri_base_url="https://s3.eu-central-2.wasabisys.com/s2-mpc/catalog",
    gri_collection="GRI_L1C",
    cache_dir="/tmp/gri_cache",
    output_dir="/tmp/gri_outputs",
    timeout=60,
    max_workers=4,
)

# Create resolver
resolver = GRIResolver(cfg)

# Resolve by tiles
result = resolver.resolve_tiles(["31UDQ", "33MUV"], limit=2)
print(result.to_dict())
```

## Configuration

Class: `ResolverConfig`
- `gri_base_url` (str): Static catalog root URL
- `gri_collection` (str): Collection subfolder (e.g., `GRI_L1C`)
- `cache_dir` (Path): Local cache state (manifests)
- `output_dir` (Path): Image extraction output
- `timeout` (int): HTTP timeout (s)
- `cache_ttl_hours` (int): TTL for cache entries
- `force` (bool): Ignore cache and re-download
- `max_workers` (int): Parallel downloads (>=2 enables concurrency)

Environment variables are supported (e.g., `GRI_BASE_URL`, `GRI_MAX_WORKERS`).

## Core APIs

### `GRIResolver.resolve_tiles(tiles, *, limit=None, force=False, progress_cb=None) -> ResolveResult`
- Resolve items by MGRS tile IDs
- `limit`: max number of items globally
- `force`: ignore cache
- `progress_cb`: optional callable `str -> None` for textual updates (bar UI is internal)
- Returns `ResolveResult` with:
  - `mgrs_tiles`, `gri_items`, `unresolved_tiles`
  - `downloaded_files`, `failed_files`
  - `downloaded_items`, `failed_items`
  - `download_dir`, `cache_dir`

### `GRIResolver.resolve_roi(bounds, *, sample_points=500, limit=None, force=False, progress_cb=None)`
- Resolve items for a ROI `[min_lon, min_lat, max_lon, max_lat]`
- Computes covering tiles using sampling, then delegates to `resolve_tiles`

### `GRIResolver.resolve_region(region, *, sample_points=500, limit=None, force=False, progress_cb=None)`
- Resolve items for a predefined region (see `gri_resolver/regions.py`)

## Investigation APIs

```python
from gri_resolver.investigate import Investigator
inv = Investigator(cfg)

# Presence: {tile: bool}
pres = inv.check_presence_for_tiles(["31UDQ", "33MUV"])

# Inspect: {tile: [items]}
items_by_tile = inv.inspect_items_for_tiles(["31UDQ"], limit_per_tile=3)
```

- Presence uses a fast HEAD on `*_item.json` and is non-destructive.
- Inspect fetches metadata (no downloads).

## Download & Cache Behavior

- The resolver prefers archive assets (`.tar.gz`) and extracts the first image (`.tif/.jp2`).
- Direct image assets are downloaded as-is.
- Cache manifest maps item IDs → extracted image paths; `force=True` bypasses cache.
- Parallelism: set `max_workers >= 2` to enable concurrent downloads.

## Progress & UI

- When `progress_cb` is set and `max_workers > 1`, the resolver displays:
  - A global “Tiles” bar for discovery (ROI/region)
  - A global “Bytes” bar for cumulative download with current tiles postfix
- In serial mode, per-item download bar and extracting stage are displayed.

## Error Handling

- Network errors and missing assets are logged and counted in `failed_items`/`failed_files`.
- The resolver continues processing other items/tiles.

## Extensibility Points

- Tile discovery: `gri_resolver/integrations/stac_mgrs.py`
- Finder (catalog access): `gri_resolver/integrations/gri_finder.py`
  - Fast path uses HEAD on `*_item.json` then GET; deep scans are disabled by default
- Downloader/extractor: `gri_resolver/downloader.py`
- Cache index: `gri_resolver/cache.py` (thread-safe manifest updates)

## Minimal Example (end-to-end)

```python
from gri_resolver import GRIResolver, ResolverConfig

cfg = ResolverConfig(max_workers=4)
resolver = GRIResolver(cfg)
res = resolver.resolve_region("gabon", sample_points=600, limit=5)
for p in res.downloaded_files:
    print("downloaded:", p)
```

## CLI Commands

The `gri-resolve` CLI provides several commands for different use cases:

- `resolve`: Resolve and download images by tiles/ROI/region
- `presence`: Check if items exist for tiles (fast HEAD requests)
- `inspect`: List metadata for items without downloading
- `coverage`: List tiles covering a region/ROI
- `version`: Display package version (simple or detailed JSON)
- `check`: Perform health checks on GRI service availability
- `serve`: Start web interface server

### Exit Codes

The `check` command uses exit codes for scripting and CI integration:
- Exit code `0`: All checks passed (service is available)
- Exit code `1`: One or more checks failed (service unavailable)

Example usage in scripts:
```bash
#!/bin/bash
if gri-resolve check; then
    echo "GRI service is available"
    # Proceed with operations
else
    echo "GRI service is unavailable"
    exit 1
fi
```

## Notes

- ZIP archives are not yet supported (warning emitted if encountered).
- For very large ROIs, use `presence` first to filter only existing tiles.
