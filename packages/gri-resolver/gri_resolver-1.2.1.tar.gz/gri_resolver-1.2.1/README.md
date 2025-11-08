# gri_resolver

[![pipeline status](https://git2.gael.fr/gael10/amalfi/amalfi-third-party/gri-resolver/badges/main/pipeline.svg)](https://git2.gael.fr/gael10/amalfi/amalfi-third-party/gri-resolver/-/pipelines)
[![coverage report](https://git2.gael.fr/gael10/amalfi/amalfi-third-party/gri-resolver/badges/main/coverage.svg)](https://git2.gael.fr/gael10/amalfi/amalfi-third-party/gri-resolver/-/commits/main)

Tile-based GRI resolver, downloader, cache, and investigation tools.
- No runtime dependency on gcp_creator
- Tile-first resolution (no full catalog scan)
- Robust caching and optional force re-download
- Automatic quality-based selection (best image per tile)
- CLI with progress bars and JSON outputs
- **Web interface** for interactive tile management, visualization, and downloads

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e .
```

## Configuration

Defaults (override via CLI flags or env):
- GRI_BASE_URL (default `https://s3.eu-central-2.wasabisys.com/s2-mpc/catalog`)
- GRI_COLLECTION (default `GRI_L1C`)
- GRI_CACHE_DIR (default `<repo>/gri_resolver/cache`)
- GRI_OUTPUT_DIR (default `<repo>/gri_resolver/outputs`)
- GRI_TIMEOUT (default 60s)
- GRI_CACHE_TTL_HOURS (default 168h)
- GRI_FORCE=1 to ignore cache
- GRI_MAX_WORKERS (default 4)
- GRI_QUALITY_SELECTION (default 1, set to 0 to disable automatic quality selection)
- GRI_KEEP_MULTIPLE_PER_TILE (default 1, keeps historical images per tile)
- GRI_PREFER_RECENT (default 0, set to 1 to prefer more recent images in scoring)

Show current config:
```bash
gri-resolve resolve --show-config --json
```

## CLI Overview

```bash
gri-resolve --help
```

### Resolve and download

Resolve by tiles/ROI/region, download archives/images, and cache results.
```bash
# By tile(s)
gri-resolve resolve --tiles 31UDQ 33MUV --gri-base-url https://.../catalog --gri-collection GRI_L1C --progress

# By ROI (min_lon min_lat max_lon max_lat)
gri-resolve resolve --roi 2.0 48.0 3.0 49.0 --limit 3 --progress

# By region (predefined)
gri-resolve resolve --region gabon --limit 5 --progress

# Parallel downloads (e.g., 6 workers)
gri-resolve resolve --tiles 31UDQ 33MUV --max-workers 6 --progress
```
Outputs a summary (and JSON if `--json` or `--report path.json`).

Progress:
- “Tiles” bar for discovery (region/ROI)
- “Bytes” bar (parallel mode): cumulative download progress, with active tiles listed
- Per-item bar (serial mode): bytes + extracting stage

### Presence (existence check by tile)

```bash
# By tiles
gri-resolve presence --tiles 31UDQ 33MUV --json

# By region / ROI (tiles computed then checked)
gri-resolve presence --region germany --json
gri-resolve presence --roi -5 41 10 51 --json

# Progress streaming (NDJSON)
gri-resolve presence --tiles 31UDQ 33MUV --progress --json --stream-json
```

### Inspect (list metadata only)

```bash
# Tiles
gri-resolve inspect --tiles 31UDQ 33MUV --limit-per-tile 2 --json
# Region / ROI
gri-resolve inspect --region france --json
gri-resolve inspect --roi 2 48 3 49 --json
```

### Coverage (list tiles only)

```bash
gri-resolve coverage --region gabon --json
gri-resolve coverage --roi -5 41 10 51 --json
```

### Version

Display the package version:

```bash
# Show version only
gri-resolve version

# Show detailed version information (JSON)
gri-resolve version --json
```

### Check Service Availability

Perform comprehensive health checks on the GRI service:

```bash
# Check GRI service availability
gri-resolve check

# Check with custom test tile
gri-resolve check --test-tile 31UDQ

# Check with JSON output
gri-resolve check --json

# Check with custom base URL and collection
gri-resolve check --gri-base-url https://.../catalog --gri-collection GRI_L1C
```

The `check` command performs three checks:
1. **Base URL**: Verifies the GRI catalog base URL is accessible
2. **Collection**: Verifies the specified collection is accessible
3. **Tile Access**: Verifies that items can be retrieved for a test tile (default: 30TWT)

Exit codes:
- `0` if all checks pass
- `1` if any check fails

This allows use in scripts and CI: `gri-resolve check && echo "Service is up"`

### Web Interface

Start a web server for interactive tile management:

```bash
# Start server on default host/port (127.0.0.1:8000)
gri-resolve serve

# Custom host and port
gri-resolve serve --host 0.0.0.0 --port 8080

# Enable auto-reload for development
gri-resolve serve --reload
```

Then open `http://localhost:8000` in your browser.

**Features:**
- **Interactive map** for ROI selection with MGRS tile overlay
- **Download tiles** by tile codes, ROI (drawn on map or coordinates), or predefined regions
- **Real-time progress** tracking with detailed activity log and byte-level progress bars
- **Visualize cached images** with previews (JP2/TIF supported via conversion)
- **Rate images** (0-5 stars) to mark favorites
- **Delete images or entire tiles** from cache
- **Storage information** dashboard showing disk usage, file counts, and top tiles by size
- **Quicklook previews** of top-rated images in tile listings
- **Lazy loading** of images for better performance

### Regions

Some predefined regions exist (Africa subset + Europe quick bboxes). List them:
```bash
gri-resolve resolve --list-regions --json
```

## API (Python)

```python
from gri_resolver import GRIResolver, ResolverConfig

resolver = GRIResolver(ResolverConfig())
res = resolver.resolve_tiles(["31UDQ"], limit=1)
print(res.to_dict())
```

## Notes & Behavior

- **Resolution is tile-first**: we try `*_item.json` via HEAD/GET; deep catalog scan is disabled by default for speed.
- **Quality selection**: When multiple items exist for a tile, the resolver automatically selects the best one. Selection priority:
  1. **User rating** (if any image has been rated by the user, prefer the highest rated)
  2. **Quality score** (computed from metadata when no user ratings exist):
     - Cloud cover (lower is better, if available in `eo:cloud_cover`)
     - Sun elevation angle (higher is better, if available in `view:sun_elevation`)
     - Recency (optional, if `GRI_PREFER_RECENT=1`)
  Items without quality metadata receive a low but non-zero score and are still downloaded.
- **Caching**: items already extracted are reused unless `--force`/`GRI_FORCE=1`. The cache stores:
  - Quality scores and metadata for automatic selection
  - User ratings (0-5 stars) for manual curation
  - Multiple images per tile (historical) when `GRI_KEEP_MULTIPLE_PER_TILE=1`
  The cache always returns the best image (prioritizing user ratings, then quality scores).
- **Multiple images per tile**: by default, the cache keeps multiple images per tile (historical), but always returns the best one. Set `GRI_KEEP_MULTIPLE_PER_TILE=0` to keep only the best.
- **Archives**: `.tar.gz` supported (extracts all `.tif/.jp2/.tiff` files found); ZIP not yet supported.
- **Parallelism**: `--max-workers` controls concurrent downloads.
- **Progress**: bars disabled when `--json/--report` to keep output machine-readable. Web interface shows real-time progress with detailed activity logs.
- **Image formats**: The web interface can preview JP2 and TIF images by converting them to JPEG on-the-fly with contrast enhancement.

## Web API Endpoints

The web server exposes a REST API for programmatic access:

- `GET /` - Web interface (HTML)
- `GET /api/config` - Get current configuration
- `GET /api/tiles` - List all cached tiles with metadata
- `GET /api/tiles/{tile_code}` - Get details for a specific tile
- `GET /api/tiles/{tile_code}/images/{item_id}` - Get image file or preview (`?preview=true`)
- `POST /api/tiles/{tile_code}/images/{item_id}/rate` - Rate an image (0-5)
- `DELETE /api/tiles/{tile_code}/images/{item_id}` - Delete a specific image
- `DELETE /api/tiles/{tile_code}` - Delete all images for a tile
- `POST /api/tiles/download` - Start a download task (tiles, ROI, or region)
- `GET /api/tasks/{task_id}` - Get download task status and progress
- `GET /api/storage` - Get storage information (cache and output directories)
- `GET /api/regions` - List predefined regions
- `GET /api/geojson/tiles` - Get MGRS tiles as simplified GeoJSON (for map overlay)
- `GET /api/kml/tiles` - Get MGRS tiles as KML (legacy format)

## Troubleshooting

- **No items found for a tile**: verify the tile path exists in the catalog (e.g., `.../GRI_L1C/T31/T31U/T31UDQ_item.json`).
- **Mixed/too many tiles from ROI**: increase/decrease `--sample-points`; use `presence` to filter only existing tiles.
- **Verbosity**: use `--progress` for human-friendly bars; omit it with `--json` for clean JSON.
- **Web interface not loading**: check that the server is running and accessible at the configured host/port.
- **Image previews not showing**: ensure `pillow` and `rasterio` are installed (required for JP2/TIF conversion).
- **Slow MGRS tile layer**: the GeoJSON endpoint uses aggressive simplification and viewport-based rendering for performance.

## License

MIT License – see `LICENSE`.
