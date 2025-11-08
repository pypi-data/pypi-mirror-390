from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .config import ResolverConfig
from .resolver import GRIResolver
from .investigate import Investigator
from .regions import PREDEFINED_REGIONS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "gri-resolve",
        description="Resolve, download and investigate GRI items organized by MGRS tiles.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Common
    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--cache-dir",
            type=str,
            help="Path to local cache directory (stores manifests and state)",
        )
        p.add_argument(
            "--output-dir",
            type=str,
            help="Directory where extracted/downloaded images are written",
        )
        p.add_argument(
            "--gri-base-url",
            type=str,
            help="Base URL of the GRI static catalog (root catalog path)",
        )
        p.add_argument(
            "--gri-collection",
            type=str,
            help="Collection subfolder within the catalog (e.g., GRI_L1C)",
        )
        p.add_argument(
            "--timeout",
            type=int,
            help="HTTP timeout in seconds for catalog and asset requests",
        )
        p.add_argument(
            "--cache-ttl-hours",
            type=int,
            help="Cache TTL in hours (default: 168)",
        )
        p.add_argument(
            "--max-workers",
            type=int,
            help="Number of parallel downloads (default from config/env)",
        )
        p.add_argument(
            "--force",
            action="store_true",
            help="Ignore cache and re-download items even if already present",
        )
        quality_group = p.add_mutually_exclusive_group()
        quality_group.add_argument(
            "--quality-selection",
            action="store_true",
            dest="quality_selection_enabled",
            default=None,
            help="Enable quality-based item selection (default: enabled)",
        )
        quality_group.add_argument(
            "--no-quality-selection",
            action="store_false",
            dest="quality_selection_enabled",
            help="Disable quality-based item selection",
        )
        keep_multiple_group = p.add_mutually_exclusive_group()
        keep_multiple_group.add_argument(
            "--keep-multiple-per-tile",
            action="store_true",
            dest="keep_multiple_per_tile",
            default=None,
            help="Keep multiple items per tile (default: enabled)",
        )
        keep_multiple_group.add_argument(
            "--no-keep-multiple-per-tile",
            action="store_false",
            dest="keep_multiple_per_tile",
            help="Keep only one item per tile",
        )
        prefer_recent_group = p.add_mutually_exclusive_group()
        prefer_recent_group.add_argument(
            "--prefer-recent",
            action="store_true",
            dest="prefer_recent",
            default=None,
            help="Prefer more recent items when scoring (default: disabled)",
        )
        prefer_recent_group.add_argument(
            "--no-prefer-recent",
            action="store_false",
            dest="prefer_recent",
            help="Do not prefer recent items when scoring",
        )
        p.add_argument(
            "--json",
            action="store_true",
            help="Emit machine-readable JSON output (single JSON object)",
        )
        p.add_argument(
            "--report",
            type=str,
            help="Write JSON output to the specified file path",
        )

    # resolve
    p_resolve = sub.add_parser(
        "resolve",
        help="Resolve and download images",
        description="Resolve GRI items by region/ROI/tiles and download images with caching.",
    )
    add_common(p_resolve)
    p_resolve.add_argument("--list-regions", action="store_true")
    p_resolve.add_argument("--show-config", action="store_true")
    p_resolve.add_argument(
        "--region",
        type=str,
        help="Use a predefined region name (e.g., gabon) to compute tiles",
    )
    p_resolve.add_argument(
        "--roi",
        nargs=4,
        type=float,
        metavar=("min_lon", "min_lat", "max_lon", "max_lat"),
        help="Use a bounding box (lon/lat) to compute covering tiles",
    )
    p_resolve.add_argument(
        "--tiles",
        nargs="*",
        type=str,
        help="Resolve directly by MGRS tile IDs (e.g., 31UDQ 33MUV)",
    )
    p_resolve.add_argument(
        "--sample-points",
        type=int,
        default=500,
        help="Sampling density for ROI/region tile discovery (higher = more tiles)",
    )
    p_resolve.add_argument(
        "--limit",
        type=int,
        help="Global maximum number of items to process",
    )
    p_resolve.add_argument(
        "--progress",
        action="store_true",
        help="Print progress messages during resolution",
    )

    # presence
    p_presence = sub.add_parser(
        "presence",
        help="Check item presence",
        description="Check if GRI items exist for the given MGRS tile IDs without downloading.",
    )
    add_common(p_presence)
    p_presence.add_argument(
        "--show-config",
        action="store_true",
        help="Print current configuration and exit",
    )
    p_presence.add_argument(
        "--list-regions",
        action="store_true",
        help="List predefined regions and exit",
    )
    p_presence.add_argument(
        "--region",
        type=str,
        help="Predefined region used to compute tiles for presence check",
    )
    p_presence.add_argument(
        "--roi",
        nargs=4,
        type=float,
        metavar=("min_lon", "min_lat", "max_lon", "max_lat"),
        help="Bounding box used to compute tiles for presence check",
    )
    p_presence.add_argument(
        "--tiles",
        nargs="+",
        type=str,
        help="MGRS tile IDs to check (e.g., 31UDQ 33MUV)",
    )
    p_presence.add_argument(
        "--sample-points",
        type=int,
        default=500,
        help="Sampling density for ROI/region tile discovery",
    )
    p_presence.add_argument(
        "--progress",
        action="store_true",
        help="Print progress messages per tile as results are obtained",
    )
    p_presence.add_argument(
        "--stream-json",
        action="store_true",
        help="With --json and --progress, emit one JSON object per line (NDJSON)",
    )

    # inspect
    p_inspect = sub.add_parser(
        "inspect",
        help="Inspect items",
        description="List GRI items for the given tiles (metadata only), no downloads.",
    )
    add_common(p_inspect)
    p_inspect.add_argument(
        "--region",
        type=str,
        help="Predefined region used to compute tiles for inspection",
    )
    p_inspect.add_argument(
        "--roi",
        nargs=4,
        type=float,
        metavar=("min_lon", "min_lat", "max_lon", "max_lat"),
        help="Bounding box used to compute tiles for inspection",
    )
    p_inspect.add_argument(
        "--tiles",
        nargs="+",
        type=str,
        help="MGRS tile IDs to inspect (metadata only)",
    )
    p_inspect.add_argument(
        "--sample-points",
        type=int,
        default=500,
        help="Sampling density for ROI/region tile discovery",
    )
    p_inspect.add_argument(
        "--limit-per-tile",
        type=int,
        help="Maximum items to list per tile",
    )

    # coverage
    p_cov = sub.add_parser(
        "coverage",
        help="List coverage tiles",
        description="Compute and list MGRS tiles covering a region or ROI, or echo given tiles.",
    )
    add_common(p_cov)
    p_cov.add_argument(
        "--region",
        type=str,
        help="Predefined region for which to compute covering tiles",
    )
    p_cov.add_argument(
        "--roi",
        nargs=4,
        type=float,
        metavar=("min_lon", "min_lat", "max_lon", "max_lat"),
        help="Bounding box (lon/lat) for which to compute covering tiles",
    )
    p_cov.add_argument(
        "--tiles",
        nargs="*",
        type=str,
        help="Echo these tiles (useful to normalize/pipeline)",
    )

    # serve
    p_serve = sub.add_parser(
        "serve",
        help="Start web API server",
        description="Start a FastAPI web server for managing tiles and cached images.",
    )
    add_common(p_serve)
    p_serve.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    p_serve.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    p_serve.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    # version
    p_version = sub.add_parser(
        "version",
        help="Show package version",
        description="Display the package version. Use --json for detailed information.",
    )
    p_version.add_argument(
        "--json",
        action="store_true",
        help="Output version information as JSON",
    )

    # check
    p_check = sub.add_parser(
        "check",
        help="Check GRI service availability",
        description="Perform comprehensive health checks on the GRI service.",
    )
    add_common(p_check)
    p_check.add_argument(
        "--test-tile",
        type=str,
        default="30TWT",
        help="MGRS tile to use for access test (default: 30TWT)",
    )
    p_check.add_argument(
        "--fast",
        action="store_true",
        help="Fast check: only verify HEAD request on collection",
    )
    p_check.add_argument(
        "--quiet",
        action="store_true",
        help="Quiet mode: suppress all output, only return exit code",
    )

    return parser.parse_args(argv)


def load_config_from_args(args: argparse.Namespace) -> ResolverConfig:
    cfg = ResolverConfig()
    if hasattr(args, "cache_dir") and args.cache_dir:
        cfg.cache_dir = Path(args.cache_dir)
    if hasattr(args, "output_dir") and args.output_dir:
        cfg.output_dir = Path(args.output_dir)
    if hasattr(args, "gri_base_url") and args.gri_base_url:
        cfg.gri_base_url = args.gri_base_url
    if getattr(args, "gri_collection", None):
        cfg.gri_collection = args.gri_collection
    if hasattr(args, "timeout") and args.timeout:
        cfg.timeout = int(args.timeout)
    if hasattr(args, "cache_ttl_hours") and args.cache_ttl_hours is not None:
        cfg.cache_ttl_hours = int(args.cache_ttl_hours)
    if getattr(args, "max_workers", None) is not None:
        cfg.max_workers = int(args.max_workers)
    if hasattr(args, "force") and args.force:
        cfg.force = True
    if hasattr(args, "quality_selection_enabled") and args.quality_selection_enabled is not None:
        cfg.quality_selection_enabled = args.quality_selection_enabled
    if hasattr(args, "keep_multiple_per_tile") and args.keep_multiple_per_tile is not None:
        cfg.keep_multiple_per_tile = args.keep_multiple_per_tile
    if hasattr(args, "prefer_recent") and args.prefer_recent is not None:
        cfg.prefer_recent = args.prefer_recent
    return cfg


def print_or_report(obj, as_json: bool, report_path: str | None) -> None:
    if as_json or report_path:
        payload = json.dumps(obj, indent=2)
        if report_path:
            with open(report_path, "w") as f:
                f.write(payload)
        if as_json:
            print(payload)
    else:
        # Minimal text output
        if isinstance(obj, dict):
            for k, v in obj.items():
                print(f"{k}: {v}")
        else:
            print(obj)


def check_gri_service(cfg: ResolverConfig, test_tile: str, fast: bool = False) -> Dict[str, Any]:
    """Perform comprehensive health checks on the GRI service.

    Args:
        cfg: Resolver configuration
        test_tile: MGRS tile code to use for access test
        fast: If True, only perform HEAD check on collection

    Returns:
        Dictionary with check results.
    """
    from .integrations.gri_finder import GRIFinder
    from .logging import get_logger
    import time

    logger = get_logger(__name__)
    finder = GRIFinder({
        "catalog_url": cfg.gri_base_url,
        "collection": cfg.gri_collection,
        "timeout": cfg.timeout,
    }, logger)

    # Build correct URLs
    base_url = f"{cfg.gri_base_url.rstrip('/')}/catalog.json"
    collection_url = f"{cfg.gri_base_url.rstrip('/')}/{cfg.gri_collection}/collection.json"

    report = {
        "base_url": {"status": "error", "url": base_url, "message": ""},
        "collection": {"status": "error", "url": collection_url, "message": ""},
        "tile_access": {"status": "error", "tile": test_tile, "items_found": 0, "message": ""},
        "overall": "error",
        "fast": fast,
    }

    if fast:
        # Fast mode: only check collection
        report["collection"]["url"] = collection_url
        try:
            start_time = time.time()
            if finder._http_head_exists(collection_url):
                elapsed = time.time() - start_time
                report["collection"]["status"] = "ok"
                report["collection"]["message"] = f"Accessible (response time: {elapsed:.2f}s)"
            else:
                report["collection"]["message"] = "Not accessible (HEAD request failed)"
        except Exception as e:
            report["collection"]["message"] = f"Error: {str(e)}"

        # Overall status based only on collection in fast mode
        report["overall"] = "ok" if report["collection"]["status"] == "ok" else "error"
        return report

    # Full check mode
    # Check 1: Base URL
    report["base_url"]["url"] = base_url
    try:
        start_time = time.time()
        if finder._http_head_exists(base_url):
            elapsed = time.time() - start_time
            report["base_url"]["status"] = "ok"
            report["base_url"]["message"] = f"Accessible (response time: {elapsed:.2f}s)"
        else:
            report["base_url"]["message"] = "Not accessible (HEAD request failed)"
    except Exception as e:
        report["base_url"]["message"] = f"Error: {str(e)}"

    # Check 2: Collection
    report["collection"]["url"] = collection_url
    try:
        start_time = time.time()
        if finder._http_head_exists(collection_url):
            elapsed = time.time() - start_time
            report["collection"]["status"] = "ok"
            report["collection"]["message"] = f"Accessible (response time: {elapsed:.2f}s)"
        else:
            report["collection"]["message"] = "Not accessible (HEAD request failed)"
    except Exception as e:
        report["collection"]["message"] = f"Error: {str(e)}"

    # Check 3: Tile access
    try:
        start_time = time.time()
        items = finder.search_by_mgrs_tile(test_tile, limit=1)
        elapsed = time.time() - start_time
        if items:
            report["tile_access"]["status"] = "ok"
            report["tile_access"]["items_found"] = len(items)
            report["tile_access"]["message"] = f"Found {len(items)} item(s) (response time: {elapsed:.2f}s)"
        else:
            report["tile_access"]["message"] = f"No items found for tile {test_tile}"
    except Exception as e:
        report["tile_access"]["message"] = f"Error: {str(e)}"

    # Determine overall status
    if all([
        report["base_url"]["status"] == "ok",
        report["collection"]["status"] == "ok",
        report["tile_access"]["status"] == "ok",
    ]):
        report["overall"] = "ok"
    else:
        report["overall"] = "error"

    return report


def main() -> None:
    args = parse_args()
    cfg = load_config_from_args(args)

    if args.cmd == "resolve":
        if getattr(args, "list_regions", False):
            data = {k: {"name": v["name"], "bounds": v["bounds"]} for k, v in PREDEFINED_REGIONS.items()}
            print_or_report(data, True if getattr(args, "json", False) else False, getattr(args, "report", None))
            return
        if getattr(args, "show_config", False):
            data = {
                "gri_base_url": cfg.gri_base_url,
                "gri_collection": cfg.gri_collection,
                "cache_dir": str(cfg.cache_dir),
                "output_dir": str(cfg.output_dir),
                "timeout": cfg.timeout,
                "cache_ttl_hours": cfg.cache_ttl_hours,
                "max_workers": cfg.max_workers,
                "force": cfg.force or getattr(args, "force", False),
                "quality_selection_enabled": cfg.quality_selection_enabled,
                "keep_multiple_per_tile": cfg.keep_multiple_per_tile,
                "prefer_recent": cfg.prefer_recent,
            }
            print_or_report(data, True if getattr(args, "json", False) else False, getattr(args, "report", None))
            return
        api = GRIResolver(cfg)
        use_tqdm = getattr(args, "progress", False) and not args.json and not args.report
        if args.tiles:
            result = api.resolve_tiles(args.tiles, limit=args.limit, force=args.force, use_tqdm=use_tqdm)
        elif args.roi:
            result = api.resolve_roi(
                tuple(args.roi),
                sample_points=args.sample_points,
                limit=args.limit,
                force=args.force,
                use_tqdm=use_tqdm,
            )
        elif args.region:
            result = api.resolve_region(
                args.region,
                sample_points=args.sample_points,
                limit=args.limit,
                force=args.force,
                use_tqdm=use_tqdm,
            )
        else:
            print("Error: one of --tiles, --roi, or --region is required", file=sys.stderr)
            sys.exit(2)
        print_or_report(result.to_dict(), args.json, args.report)
        return

    if args.cmd == "presence":
        if getattr(args, "show_config", False):
            data = {
                "gri_base_url": cfg.gri_base_url,
                "gri_collection": cfg.gri_collection,
                "cache_dir": str(cfg.cache_dir),
                "output_dir": str(cfg.output_dir),
                "timeout": cfg.timeout,
                "cache_ttl_hours": cfg.cache_ttl_hours,
                "max_workers": cfg.max_workers,
                "force": cfg.force,
                "quality_selection_enabled": cfg.quality_selection_enabled,
                "keep_multiple_per_tile": cfg.keep_multiple_per_tile,
                "prefer_recent": cfg.prefer_recent,
            }
            print_or_report(data, True if getattr(args, "json", False) else False, getattr(args, "report", None))
            return
        if getattr(args, "list_regions", False):
            data = {k: {"name": v["name"], "bounds": v["bounds"]} for k, v in PREDEFINED_REGIONS.items()}
            print_or_report(data, True if getattr(args, "json", False) else False, getattr(args, "report", None))
            return
        tiles = args.tiles or []
        if not tiles and args.roi:
            from .tiles import list_tiles_for_roi
            tiles = list_tiles_for_roi(tuple(args.roi), sample_points=args.sample_points)
        if not tiles and args.region:
            from .regions import get_region_bounds
            b = get_region_bounds(args.region)
            if b:
                from .tiles import list_tiles_for_roi
                tiles = list_tiles_for_roi(b, sample_points=args.sample_points)
        if not tiles:
            print(
                "Error: one of --tiles, --roi or --region is required (or use --show-config/--list-regions)",
                file=sys.stderr,
            )
            sys.exit(2)
        inv = Investigator(cfg)
        if args.progress and args.json and args.stream_json:
            import json as _json
            for t in tiles:
                pr = inv.check_presence_for_tiles([t])
                print(_json.dumps({t: pr.get(t)}))
        elif args.progress and not args.json and not args.report:
            for t in tiles:
                pr = inv.check_presence_for_tiles([t])
                print(f"{t}: {pr.get(t)}")
        else:
            out = inv.check_presence_for_tiles(tiles)
            print_or_report(out, args.json, args.report)
        return

    if args.cmd == "inspect":
        inv = Investigator(cfg)
        tiles = args.tiles or []
        if not tiles and args.roi:
            from .tiles import list_tiles_for_roi
            tiles = list_tiles_for_roi(tuple(args.roi), sample_points=args.sample_points)
        if not tiles and args.region:
            from .regions import get_region_bounds
            b = get_region_bounds(args.region)
            if b:
                from .tiles import list_tiles_for_roi
                tiles = list_tiles_for_roi(b, sample_points=args.sample_points)
        if not tiles:
            print("Error: one of --tiles, --roi or --region is required", file=sys.stderr)
            sys.exit(2)
        out = inv.inspect_items_for_tiles(tiles, args.limit_per_tile)
        print_or_report(out, args.json, args.report)
        return

    if args.cmd == "coverage":
        from .tiles import list_tiles_for_roi
        from .regions import get_region_bounds
        tiles = []
        bounds = None
        if args.tiles:
            tiles = args.tiles
        elif args.roi:
            bounds = tuple(args.roi)
            tiles = list_tiles_for_roi(bounds)
        elif args.region:
            bounds = get_region_bounds(args.region)
            if bounds:
                tiles = list_tiles_for_roi(bounds)
        out = {
            "tile_count": len(tiles),
            "tiles": tiles,
            "bounds": bounds,
        }
        print_or_report(out, args.json, args.report)
        return

    if args.cmd == "serve":
        import uvicorn
        from .web_api import create_app

        app = create_app(cfg)
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
        return

    if args.cmd == "version":
        # Try to get version from installed package metadata first (works for distributed packages)
        version_str = "unknown"
        try:
            # Python 3.8+
            from importlib.metadata import version
            version_str = version("gri_resolver")
        except ImportError:
            # Python < 3.8 fallback
            try:
                import pkg_resources
                version_str = pkg_resources.get_distribution("gri_resolver").version
            except Exception:
                pass
        except Exception:
            # If metadata lookup fails, try setuptools_scm (for development)
            try:
                from setuptools_scm import get_version
                version_str = get_version()
            except Exception:
                pass

        if args.json:
            # Detailed JSON output
            version_info: Dict[str, Any] = {
                "package": "gri_resolver",
                "version": version_str,
            }
            # Try to get additional git metadata if in development
            try:
                from setuptools_scm import get_version
                git_version = get_version()
                version_info["git_version"] = git_version
                # Extract tag if available (version usually contains tag info)
                if version_str and not version_str.startswith("0.0.0"):
                    version_info["git_tag"] = version_str.split("+")[0] if "+" in version_str else version_str
            except Exception:
                pass
            print_or_report(version_info, True, None)
        else:
            # Simple text output
            print(version_str)
        return

    if args.cmd == "check":
        test_tile = getattr(args, "test_tile", "30TWT")
        fast = getattr(args, "fast", False)
        quiet = getattr(args, "quiet", False)
        report = check_gri_service(cfg, test_tile, fast=fast)

        if quiet:
            # Quiet mode: no output, only exit code
            pass
        elif args.json:
            print_or_report(report, True, None)
        else:
            # Text mode: formatted report
            print("GRI Service Health Check" + (" (Fast Mode)" if fast else ""))
            print("=" * 50)
            if not fast:
                print(f"\nBase URL: {report['base_url']['status'].upper()}")
                print(f"  URL: {report['base_url']['url']}")
                print(f"  {report['base_url']['message']}")
            print(f"\nCollection: {report['collection']['status'].upper()}")
            print(f"  URL: {report['collection']['url']}")
            print(f"  {report['collection']['message']}")
            if not fast:
                print(f"\nTile Access: {report['tile_access']['status'].upper()}")
                print(f"  Tile: {report['tile_access']['tile']}")
                print(f"  Items found: {report['tile_access']['items_found']}")
                print(f"  {report['tile_access']['message']}")
            print(f"\nOverall Status: {report['overall'].upper()}")

        # Exit code: 0 for success, 1 for failure
        sys.exit(0 if report["overall"] == "ok" else 1)


if __name__ == "__main__":
    main()
