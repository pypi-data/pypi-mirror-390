from __future__ import annotations

import io
import json
import shutil
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import ResolverConfig
from .logging import get_logger
from .regions import PREDEFINED_REGIONS
from .resolver import GRIResolver

# Global state for download tasks
download_tasks: Dict[str, Dict[str, Any]] = {}


def create_app(config: Optional[ResolverConfig] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="GRI Resolver Web API", version="1.0.0")
    cfg = config or ResolverConfig()
    resolver = GRIResolver(cfg)
    # Use the same cache instance as the resolver to avoid duplication
    cache = resolver._cache
    logger = get_logger(__name__)

    # Setup templates
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))

    # Setup static files
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Serve the main web interface."""
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/config")
    async def get_config():
        """Get current configuration."""
        return {
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

    @app.get("/api/regions")
    async def get_regions():
        """Get list of predefined regions."""
        return {
            "regions": {
                k: {"name": v["name"], "bounds": v["bounds"], "description": v.get("description", "")}
                for k, v in PREDEFINED_REGIONS.items()
            }
        }

    @app.get("/api/storage")
    async def get_storage_info():
        """Get storage information for cache and output directories."""
        def format_bytes(bytes_size: int) -> str:
            """Format bytes to human-readable format."""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.2f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.2f} PB"

        def get_dir_size(path: Path) -> Dict[str, Any]:
            """Calculate directory size and file statistics."""
            total_size = 0
            file_count = 0
            file_types = defaultdict(int)
            file_type_sizes = defaultdict(int)

            if not path.exists():
                return {
                    "total_size": 0,
                    "total_size_formatted": "0 B",
                    "file_count": 0,
                    "file_types": {},
                    "file_type_sizes": {},
                }

            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        try:
                            size = item.stat().st_size
                            total_size += size
                            file_count += 1

                            # Track by file extension
                            ext = item.suffix.lower() or ".noext"
                            file_types[ext] += 1
                            file_type_sizes[ext] += size
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
            except (OSError, PermissionError) as e:
                logger.warning(f"Error scanning directory {path}: {e}")

            return {
                "total_size": total_size,
                "total_size_formatted": format_bytes(total_size),
                "file_count": file_count,
                "file_types": dict(file_types),
                "file_type_sizes": {
                    k: {"size": v, "size_formatted": format_bytes(v)} for k, v in file_type_sizes.items()
                },
            }

        def get_disk_usage(path: Path) -> Dict[str, Any]:
            """Get disk usage information for the path."""
            try:
                usage = shutil.disk_usage(path)
                return {
                    "total": usage.total,
                    "total_formatted": format_bytes(usage.total),
                    "used": usage.used,
                    "used_formatted": format_bytes(usage.used),
                    "free": usage.free,
                    "free_formatted": format_bytes(usage.free),
                    "percent_used": round((usage.used / usage.total) * 100, 2) if usage.total > 0 else 0,
                }
            except Exception as e:
                logger.warning(f"Error getting disk usage for {path}: {e}")
                return {
                    "total": 0,
                    "total_formatted": "Unknown",
                    "used": 0,
                    "used_formatted": "Unknown",
                    "free": 0,
                    "free_formatted": "Unknown",
                    "percent_used": 0,
                }

        # Reload cache to get latest entries
        cache.reload()

        # Get cache directory info
        cache_info = get_dir_size(cfg.cache_dir)

        # Get output directory info
        output_info = get_dir_size(cfg.output_dir)

        # Get disk usage for cache directory
        disk_usage = get_disk_usage(cfg.cache_dir)

        # Calculate size by tile
        tile_sizes: Dict[str, int] = {}
        tile_file_counts: Dict[str, int] = defaultdict(int)

        for item_id, entry in cache._index.items():
            if isinstance(entry, dict):
                tile_code = entry.get("tile")
                path_str = entry.get("path")
                if tile_code and path_str:
                    file_path = Path(path_str)
                    if file_path.exists():
                        try:
                            size = file_path.stat().st_size
                            tile_sizes[tile_code] = tile_sizes.get(tile_code, 0) + size
                            tile_file_counts[tile_code] += 1
                        except (OSError, PermissionError):
                            pass

        # Format tile sizes
        tile_sizes_formatted = {
            tile: {
                "size": size,
                "size_formatted": format_bytes(size),
                "file_count": tile_file_counts[tile],
            }
            for tile, size in sorted(tile_sizes.items(), key=lambda x: x[1], reverse=True)
        }

        # Get manifest size
        manifest_size = 0
        if cache.manifest.exists():
            try:
                manifest_size = cache.manifest.stat().st_size
            except (OSError, PermissionError):
                pass

        return {
            "cache_dir": {
                "path": str(cfg.cache_dir),
                **cache_info,
                "manifest_size": manifest_size,
                "manifest_size_formatted": format_bytes(manifest_size),
            },
            "output_dir": {
                "path": str(cfg.output_dir),
                **output_info,
            },
            "disk_usage": disk_usage,
            "tile_sizes": tile_sizes_formatted,
            "total_tiles": len(tile_sizes),
            "total_cached_items": len(cache._index),
        }

    @app.get("/api/kml/tiles")
    async def get_kml_tiles():
        """Serve the KML file with all MGRS tiles (for backward compatibility)."""
        # KML file is in gri_resolver/kml/ directory
        kml_filename = "S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml"
        kml_path = Path(__file__).parent / "kml" / kml_filename
        if not kml_path.exists():
            raise HTTPException(status_code=404, detail=f"KML file not found at {kml_path}")

        return FileResponse(
            kml_path,
            media_type="application/vnd.google-earth.kml+xml",
            filename="mgrs_tiles.kml"
        )

    @app.get("/api/geojson/tiles")
    async def get_geojson_tiles():
        """Serve simplified GeoJSON of MGRS tiles for faster loading."""
        # Cache file for simplified GeoJSON
        cache_dir = cfg.cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        geojson_cache = cache_dir / "mgrs_tiles_simplified.geojson"

        # Check if cached version exists and is newer than KML
        kml_filename = "S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml"
        kml_path = Path(__file__).parent / "kml" / kml_filename

        if geojson_cache.exists() and kml_path.exists():
            kml_mtime = kml_path.stat().st_mtime
            cache_mtime = geojson_cache.stat().st_mtime
            if cache_mtime > kml_mtime:
                # Cache is valid, return it
                return Response(
                    content=geojson_cache.read_text(encoding='utf-8'),
                    media_type="application/geo+json"
                )

        # Need to convert KML to GeoJSON
        if not kml_path.exists():
            raise HTTPException(status_code=404, detail=f"KML file not found at {kml_path}")

        try:
            # Try to use fastkml or simplekml for parsing, fallback to manual parsing
            import xml.etree.ElementTree as ET

            logger.info("Converting KML to GeoJSON (this may take a while for large files)...")
            tree = ET.parse(kml_path)
            root = tree.getroot()

            # Define namespaces
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            features = []
            placemarks = root.findall('.//kml:Placemark', ns)

            for placemark in placemarks:
                name_elem = placemark.find('kml:name', ns)
                name = name_elem.text if name_elem is not None else None

                # Find coordinates in Polygon or MultiGeometry
                coordinates = None
                for polygon in placemark.findall('.//kml:Polygon', ns):
                    outer_boundary = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
                    if outer_boundary is not None and outer_boundary.text:
                        coords_text = outer_boundary.text.strip()
                        # Parse coordinates: "lon,lat,alt lon,lat,alt ..."
                        coord_pairs = []
                        for coord_str in coords_text.split():
                            parts = coord_str.split(',')
                            if len(parts) >= 2:
                                try:
                                    lon = float(parts[0])
                                    lat = float(parts[1])
                                    coord_pairs.append([lon, lat])
                                except ValueError:
                                    continue

                        if coord_pairs:
                            # Close the polygon if not already closed
                            if coord_pairs[0] != coord_pairs[-1]:
                                coord_pairs.append(coord_pairs[0])
                            coordinates = [coord_pairs]
                            break

                if coordinates:
                    feature = {
                        "type": "Feature",
                        "properties": {"name": name} if name else {},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": coordinates
                        }
                    }
                    features.append(feature)

            geojson = {
                "type": "FeatureCollection",
                "features": features
            }

            # Simplify geometries aggressively
            # For 100km x 100km tiles, we can reduce precision significantly
            # Round coordinates to 2 decimal places (~1.1 km precision) for faster rendering
            # Also reduce number of points in polygons if they have too many
            simplified_features = []
            for feature in geojson["features"]:
                if feature["geometry"]["type"] == "Polygon":
                    simplified_rings = []
                    for ring in feature["geometry"]["coordinates"]:
                        simplified_ring = []
                        prev_coord = None
                        # Simplify by removing redundant points and reducing precision
                        for coord in ring:
                            # Round to 2 decimal places (~1.1 km precision)
                            rounded_coord = [round(coord[0], 2), round(coord[1], 2)]
                            # Skip duplicate or very close points
                            if prev_coord is None or (
                                abs(rounded_coord[0] - prev_coord[0]) > 0.01 or
                                abs(rounded_coord[1] - prev_coord[1]) > 0.01
                            ):
                                simplified_ring.append(rounded_coord)
                                prev_coord = rounded_coord

                        # Ensure polygon is closed
                        if simplified_ring and simplified_ring[0] != simplified_ring[-1]:
                            simplified_ring.append(simplified_ring[0])

                        # For 100km tiles, we only need 4-5 points (rectangle-like)
                        # Keep first, middle, and last points, plus corners
                        if len(simplified_ring) > 6:
                            # Keep corners: first, ~25%, ~50%, ~75%, last
                            keep_indices = [0]
                            if len(simplified_ring) > 4:
                                keep_indices.append(len(simplified_ring) // 4)
                            keep_indices.append(len(simplified_ring) // 2)
                            if len(simplified_ring) > 4:
                                keep_indices.append(3 * len(simplified_ring) // 4)
                            keep_indices.append(len(simplified_ring) - 1)
                            simplified_ring = [simplified_ring[i] for i in keep_indices if i < len(simplified_ring)]
                            # Ensure closed
                            if simplified_ring[0] != simplified_ring[-1]:
                                simplified_ring.append(simplified_ring[0])

                        simplified_rings.append(simplified_ring)

                    feature["geometry"]["coordinates"] = simplified_rings
                simplified_features.append(feature)

            geojson["features"] = simplified_features

            # Save to cache
            geojson_cache.write_text(json.dumps(geojson), encoding='utf-8')
            logger.info(f"Converted and cached GeoJSON with {len(features)} features")

            return Response(
                content=json.dumps(geojson),
                media_type="application/geo+json"
            )

        except Exception as e:
            logger.error(f"Error converting KML to GeoJSON: {e}")
            # Fallback to serving original KML
            return FileResponse(
                kml_path,
                media_type="application/vnd.google-earth.kml+xml",
                filename="mgrs_tiles.kml"
            )

    @app.post("/api/cache/cleanup")
    async def cleanup_cache():
        """Clean up cache entries for files that no longer exist on disk."""
        result = cache.cleanup()
        return result

    @app.get("/api/tiles")
    async def list_tiles():
        """List all tiles with cached images."""
        # Clean up missing files first
        cache.cleanup()
        # Reload cache to get latest entries
        cache.reload()
        tiles_dict = cache.list_all_tiles()
        tiles_list = list(tiles_dict.values())
        tiles_list.sort(key=lambda x: x["tile_code"])

        return {"tiles": tiles_list}

    @app.get("/api/tiles/{tile_code}")
    async def get_tile_details(tile_code: str):
        """Get details for a specific tile with all its images."""
        # Clean up missing files first
        cache.cleanup()
        # Reload cache to get latest entries
        cache.reload()
        all_entries = cache.get_all_for_tile(tile_code)
        if not all_entries:
            raise HTTPException(status_code=404, detail=f"Tile {tile_code} not found in cache")

        # Group images by base item_id (remove _imgX suffix)
        grouped_images: Dict[str, List[Dict[str, Any]]] = {}
        for entry in all_entries:
            item_id = entry.get("item_id", "")
            # Remove _imgX suffix to get base item_id
            base_item_id = item_id.rsplit("_img", 1)[0] if "_img" in item_id else item_id

            if base_item_id not in grouped_images:
                grouped_images[base_item_id] = []
            grouped_images[base_item_id].append(entry)

        # Convert to list format with image groups
        images_list = []
        for base_item_id, image_entries in grouped_images.items():
            # Sort by item_id to have main image first
            image_entries.sort(key=lambda x: x.get("item_id", ""))
            images_list.append({
                "item_id": base_item_id,
                "images": image_entries,
                "image_count": len(image_entries),
            })

        # Sort by base item_id
        images_list.sort(key=lambda x: x["item_id"])

        return {
            "tile_code": tile_code,
            "item_count": len(images_list),
            "total_image_count": len(all_entries),
            "items": images_list,
        }

    @app.get("/api/tiles/{tile_code}/images/{item_id}")
    async def get_image_file(tile_code: str, item_id: str, preview: bool = False):
        """Serve an image file.

        item_id can be the base item_id or item_id_imgX for multiple images.
        If preview=True, converts JP2/TIF to JPEG for browser display.
        """
        # Reload cache to get latest entries (in case CLI downloaded something)
        cache.reload()
        info = cache.get_image_info(item_id)
        if not info:
            raise HTTPException(status_code=404, detail=f"Image {item_id} not found")

        path = Path(info["path"])
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Image file not found: {path}")

        # Determine media type based on file extension
        suffix_lower = path.suffix.lower()

        # If preview is requested and file is JP2 or TIFF, convert to JPEG
        if preview and suffix_lower in (".jp2", ".j2k", ".tif", ".tiff"):
            # Check if cached preview exists and is up-to-date
            preview_path = path.parent / f"{path.stem}.preview.jpg"
            original_mtime = path.stat().st_mtime if path.exists() else 0

            # If preview exists and is newer than original, serve it directly
            if preview_path.exists():
                try:
                    preview_mtime = preview_path.stat().st_mtime
                    if preview_mtime >= original_mtime:
                        # Preview is up-to-date, serve it
                        return FileResponse(
                            str(preview_path),
                            media_type="image/jpeg",
                            headers={"Cache-Control": "public, max-age=31536000"}  # Cache for 1 year
                        )
                except OSError:
                    # If we can't check mtime, regenerate preview
                    pass

            # Preview doesn't exist or is outdated, generate it
            try:
                # Try using rasterio first (better for geospatial formats)
                try:
                    import rasterio
                    import numpy as np

                    with rasterio.open(path) as src:
                        # Read the first band (or RGB if available)
                        if src.count >= 3:
                            # RGB image - use first 3 bands
                            data = np.zeros((3, src.height, src.width), dtype=np.uint8)
                            for i in range(min(3, src.count)):
                                band = src.read(i + 1)
                                # Normalize 16-bit to 8-bit using 2% and 98% percentiles for better contrast
                                # Handle both 16-bit (uint16) and 8-bit (uint8) images
                                if band.dtype == np.uint16 or band.dtype == np.int16:
                                    # 16-bit image: use percentiles for proper scaling
                                    if np.any(band > 0):
                                        p2, p98 = np.percentile(band[band > 0], [2, 98])
                                    else:
                                        p2, p98 = band.min(), band.max()
                                    if p98 > p2:
                                        band = np.clip(
                                            (band.astype(np.float32) - p2) / (p98 - p2) * 255, 0, 255
                                        ).astype(np.uint8)
                                    else:
                                        band = np.zeros_like(band, dtype=np.uint8)
                                else:
                                    # Already 8-bit or other format: simple scaling
                                    if np.any(band > 0):
                                        p2, p98 = np.percentile(band[band > 0], [2, 98])
                                    else:
                                        p2, p98 = band.min(), band.max()
                                    if p98 > p2:
                                        band = np.clip(
                                            (band.astype(np.float32) - p2) / (p98 - p2) * 255, 0, 255
                                        ).astype(np.uint8)
                                    else:
                                        band = np.zeros_like(band, dtype=np.uint8)
                                data[i] = band
                            # Convert to RGB format (height, width, channels)
                            img_data = np.transpose(data, (1, 2, 0))
                        else:
                            # Single band - convert to grayscale
                            band = src.read(1)
                            # Normalize 16-bit to 8-bit using percentiles for better contrast
                            # Handle both 16-bit (uint16) and 8-bit (uint8) images
                            if band.dtype == np.uint16 or band.dtype == np.int16:
                                # 16-bit image: use percentiles for proper scaling
                                if np.any(band > 0):
                                    p2, p98 = np.percentile(band[band > 0], [2, 98])
                                else:
                                    p2, p98 = band.min(), band.max()
                                if p98 > p2:
                                    band = np.clip(
                                        (band.astype(np.float32) - p2) / (p98 - p2) * 255, 0, 255
                                    ).astype(np.uint8)
                                else:
                                    band = np.zeros_like(band, dtype=np.uint8)
                            else:
                                # Already 8-bit or other format: simple scaling
                                if np.any(band > 0):
                                    p2, p98 = np.percentile(band[band > 0], [2, 98])
                                else:
                                    p2, p98 = band.min(), band.max()
                                if p98 > p2:
                                    band = np.clip(
                                        (band.astype(np.float32) - p2) / (p98 - p2) * 255, 0, 255
                                    ).astype(np.uint8)
                                else:
                                    band = np.zeros_like(band, dtype=np.uint8)
                            img_data = band

                        # Resize if too large (max 2048px on longest side for preview)
                        max_size = 2048
                        h, w = img_data.shape[:2] if len(img_data.shape) == 3 else img_data.shape
                        if max(h, w) > max_size:
                            ratio = max_size / max(h, w)
                            new_h, new_w = int(h * ratio), int(w * ratio)
                            # Use scipy or simple resize with numpy
                            try:
                                from scipy.ndimage import zoom
                                if len(img_data.shape) == 3:
                                    zoom_factors = (new_h / h, new_w / w, 1)
                                else:
                                    zoom_factors = (new_h / h, new_w / w)
                                img_data = zoom(img_data, zoom_factors, order=1).astype(np.uint8)
                            except ImportError:
                                # Simple downsampling if scipy not available
                                step_h, step_w = h // new_h, w // new_w
                                if len(img_data.shape) == 3:
                                    img_data = img_data[::step_h, ::step_w, :]
                                else:
                                    img_data = img_data[::step_h, ::step_w]

                        # Convert to JPEG - try multiple methods and save to cache
                        preview_data = None

                        # Method 1: Try imageio (often available with rasterio)
                        try:
                            import imageio
                            if len(img_data.shape) == 2:
                                # Grayscale - convert to RGB for JPEG
                                img_data = np.stack([img_data, img_data, img_data], axis=-1)
                            output = io.BytesIO()
                            imageio.imwrite(output, img_data, format='JPEG', quality=85)
                            preview_data = output.getvalue()
                        except (ImportError, Exception) as e:
                            if isinstance(e, ImportError):
                                pass  # Try next method
                            else:
                                logger.warning(f"imageio conversion failed: {e}, trying alternative")

                        # Method 2: Try OpenCV (cv2) if available
                        if preview_data is None:
                            try:
                                import cv2
                                if len(img_data.shape) == 2:
                                    # Grayscale
                                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
                                    _, buffer = cv2.imencode('.jpg', img_data, encode_param)
                                    preview_data = buffer.tobytes()
                                else:
                                    # RGB - convert RGB to BGR for OpenCV
                                    img_bgr = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
                                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
                                    _, buffer = cv2.imencode('.jpg', img_bgr, encode_param)
                                    preview_data = buffer.tobytes()
                            except (ImportError, Exception) as e:
                                if isinstance(e, ImportError):
                                    pass  # Try next method
                                else:
                                    logger.warning(f"OpenCV conversion failed: {e}, trying PIL")

                        # Method 3: Try PIL (with better error handling)
                        if preview_data is None:
                            try:
                                from PIL import Image
                                # Increase image size limit for large satellite images (default is ~89M pixels)
                                # Set to 500M pixels to handle very large satellite images
                                Image.MAX_IMAGE_PIXELS = 500_000_000
                                output = io.BytesIO()
                                if len(img_data.shape) == 3:
                                    img = Image.fromarray(img_data, 'RGB')
                                else:
                                    img = Image.fromarray(img_data, 'L')
                                img.save(output, format='JPEG', quality=85)
                                preview_data = output.getvalue()
                            except (ImportError, AttributeError, OSError) as pil_error:
                                error_msg = str(pil_error)
                                if '_imaging' in error_msg or 'cannot import name' in error_msg:
                                    logger.error(f"PIL/Pillow installation is corrupted: {pil_error}")
                                    raise HTTPException(
                                        status_code=500,
                                        detail=(
                                            "Image conversion failed: PIL/Pillow installation is corrupted. "
                                            "Please reinstall: pip install --force-reinstall --no-cache-dir Pillow"
                                        )
                                    )
                                else:
                                    logger.error(f"PIL conversion failed: {pil_error}")
                                    raise HTTPException(
                                        status_code=500,
                                        detail=f"Image conversion failed: {error_msg}"
                                    )

                        # Save preview to cache file
                        if preview_data:
                            try:
                                preview_path.parent.mkdir(parents=True, exist_ok=True)
                                with open(preview_path, 'wb') as f:
                                    f.write(preview_data)
                                logger.debug(f"Preview cached: {preview_path}")
                            except Exception as e:
                                logger.warning(f"Failed to cache preview: {e}")

                            # Return the preview
                            return Response(
                                content=preview_data,
                                media_type="image/jpeg",
                                headers={"Cache-Control": "public, max-age=31536000"}  # Cache for 1 year
                            )
                        else:
                            raise HTTPException(
                                status_code=500,
                                detail="Image conversion failed: All conversion methods failed"
                            )

                except ImportError:
                    # Rasterio is required for proper handling of 16-bit Sentinel-2 images
                    # PIL cannot properly handle 16-bit images, so we fail gracefully
                    logger.error("rasterio is not available. It is required for processing 16-bit Sentinel-2 images.")
                    raise HTTPException(
                        status_code=500,
                        detail=(
                            "Image conversion failed: rasterio is required for processing Sentinel-2 images. "
                            "Please install: pip install rasterio"
                        )
                    )

            except Exception as e:
                logger.error(f"Failed to convert image {path}: {e}")
                # Fall through to serve original file

        # Serve original file
        if suffix_lower in (".jpg", ".jpeg"):
            media_type = "image/jpeg"
        elif suffix_lower == ".png":
            media_type = "image/png"
        elif suffix_lower in (".jp2", ".j2k"):
            media_type = "image/jp2"
        elif suffix_lower in (".tif", ".tiff"):
            media_type = "image/tiff"
        else:
            media_type = "application/octet-stream"

        return FileResponse(path, media_type=media_type)

    @app.post("/api/tiles/identify")
    async def identify_tiles(request: Dict[str, Any]):
        """Identify tiles and items without downloading."""
        tiles = request.get("tiles", [])
        roi = request.get("roi")
        region = request.get("region")
        limit = request.get("limit")

        # Validate that at least one parameter is provided and not empty
        has_tiles = tiles and isinstance(tiles, list) and len(tiles) > 0
        has_roi = roi and isinstance(roi, list) and len(roi) == 4
        has_region = region and isinstance(region, str) and region.strip()

        if not has_tiles and not has_roi and not has_region:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Must provide at least one of: tiles (non-empty list), "
                    "roi (4 coordinates), or region (non-empty string)"
                )
            )

        try:
            # Compute tiles if needed
            # Priority order: tiles > region > ROI
            # This ensures region takes precedence over ROI if both are provided
            if has_region:
                from .regions import get_region_bounds
                bounds = get_region_bounds(region)
                if not bounds:
                    raise HTTPException(status_code=404, detail=f"Unknown region: {region}")
                from .tiles import list_tiles_for_roi
                tiles = list_tiles_for_roi(bounds, sample_points=500)
            elif has_roi:
                from .tiles import list_tiles_for_roi
                tiles = list_tiles_for_roi(tuple(roi), sample_points=500)
            # else: has_tiles is True, use tiles directly

            # Search for items in each tile
            tiles_info = []
            total_items = 0
            for tile in tiles:
                items = resolver._finder.search_by_mgrs_tile(tile, limit=None)
                item_count = len(items) if items else 0
                total_items += item_count
                tiles_info.append({
                    "tile_code": tile,
                    "item_count": item_count,
                    "items": [
                        {"id": item.get("id", ""), "datetime": item.get("properties", {}).get("datetime", "")}
                        for item in (items or [])[:5]
                    ]  # Show first 5 items as preview
                })

            # Apply limit if specified
            if limit:
                # Sort by item count (descending) and take top tiles
                tiles_info.sort(key=lambda x: x["item_count"], reverse=True)
                tiles_info = tiles_info[:limit]
                total_items = sum(t["item_count"] for t in tiles_info)

            return {
                "tiles": tiles_info,
                "total_tiles": len(tiles_info),
                "total_items": total_items,
            }
        except Exception as e:
            logger.error(f"Error identifying tiles: {e}")
            raise HTTPException(status_code=500, detail=f"Error identifying tiles: {str(e)}")

    @app.post("/api/tiles/download")
    async def download_tiles(
        request: Dict[str, Any],
        background_tasks: BackgroundTasks,
    ):
        """Trigger download of tiles."""
        task_id = str(uuid.uuid4())

        tiles = request.get("tiles", [])
        roi = request.get("roi")
        region = request.get("region")
        limit = request.get("limit")
        force = request.get("force", False)

        # Validate that at least one parameter is provided and not empty
        has_tiles = tiles and isinstance(tiles, list) and len(tiles) > 0
        has_roi = roi and isinstance(roi, list) and len(roi) == 4
        has_region = region and isinstance(region, str) and region.strip()

        if not has_tiles and not has_roi and not has_region:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Must provide at least one of: tiles (non-empty list), "
                    "roi (4 coordinates), or region (non-empty string)"
                )
            )

        # Initialize task status
        download_tasks[task_id] = {
            "status": "started",
            "progress": 0,
            "message": "Starting download...",
            "stage": "initializing",
            "details": {
                "tiles_found": 0,
                "tiles_processed": 0,
                "items_found": 0,
                "items_downloaded": 0,
                "items_failed": 0,
                "bytes_downloaded": 0,
            },
            "result": None,
            "error": None,
            "active_downloads": [],  # List of all active downloads with progress
        }

        # Track current file download progress
        current_file_progress = {"file": None, "bytes": 0, "total": 0, "percent": 0}

        def progress_callback(msg: str):
            """Callback to update task progress from resolver."""
            if task_id in download_tasks:
                download_tasks[task_id]["message"] = msg
                # Store progress messages for display
                if "progress_messages" not in download_tasks[task_id]:
                    download_tasks[task_id]["progress_messages"] = []
                download_tasks[task_id]["progress_messages"].append(msg)
                # Keep only last 50 messages
                if len(download_tasks[task_id]["progress_messages"]) > 50:
                    download_tasks[task_id]["progress_messages"] = download_tasks[task_id]["progress_messages"][-50:]

                # Parse message to extract details (only for items_found)
                # Don't count downloaded/failed items here - they are counted in the final result
                # to avoid double counting and ensure accuracy
                if "tile" in msg.lower() and "items" in msg.lower():
                    # Extract tile and item count if possible
                    import re
                    tile_match = re.search(r"tile\s+(\w+):\s*(\d+)\s+items", msg, re.IGNORECASE)
                    if tile_match:
                        download_tasks[task_id]["details"]["tiles_processed"] += 1
                        items_count = int(tile_match.group(2))
                        download_tasks[task_id]["details"]["items_found"] += items_count
                elif "download" in msg.lower() and "%" in msg:
                    # Extract download percentage
                    import re
                    pct_match = re.search(r"download\s+(\d+)%", msg, re.IGNORECASE)
                    if pct_match:
                        current_file_progress["percent"] = int(pct_match.group(1))
                        download_tasks[task_id]["current_file_progress"] = current_file_progress.copy()

        # Create a progress update callback that will be passed to _progress_update
        # Track progress per file - each download has its own progress bar
        # No locking needed: each file updates its own entry independently
        import time
        active_file_progress = {}  # file_name -> progress dict

        def create_progress_update():
            """Create a progress_update function that can be used by the resolver."""
            def progress_update(kind: str, value: int, total: int, file_name: Optional[str] = None):
                """Callback for fine-grained progress updates (bytes downloaded)."""
                if task_id not in download_tasks:
                    return

                # Use a default file name if not provided
                file_key = file_name or "unknown"
                current_time = time.time()

                if kind == "start" and total > 0:
                    # Initialize or reset progress for this specific file
                    active_file_progress[file_key] = {
                        "file": file_key,
                        "bytes": 0,
                        "total": total,
                        "percent": 0,
                        "last_update": current_time
                    }
                elif kind == "bytes" and total > 0:
                    # Update progress for the specific file
                    if file_key not in active_file_progress:
                        # Initialize if not already started
                        active_file_progress[file_key] = {
                            "file": file_key,
                            "bytes": 0,
                            "total": total,
                            "percent": 0,
                            "last_update": current_time
                        }

                    # Update bytes and percent for this file
                    active_file_progress[file_key]["bytes"] += value
                    active_file_progress[file_key]["total"] = total  # Update total in case it changed
                    active_file_progress[file_key]["percent"] = min(
                        100, int((active_file_progress[file_key]["bytes"] / total) * 100)
                    )
                    active_file_progress[file_key]["last_update"] = current_time

                    # Update total bytes downloaded
                    download_tasks[task_id]["details"]["bytes_downloaded"] += value
                elif kind == "stage":
                    # Extraction stage
                    file_key = "extracting"
                    active_file_progress[file_key] = {
                        "file": file_key,
                        "bytes": 0,
                        "total": 0,
                        "percent": 0,
                        "last_update": current_time
                    }

                # Update the list of all active downloads (for parallel display)
                # Remove finished downloads (100%) after a short delay
                # Also exclude "extracting" if it has no real progress (total = 0)
                active_downloads = []
                for file_name, progress in active_file_progress.items():
                    # Skip "extracting" if it has no real progress (total = 0 and bytes = 0)
                    if file_name == "extracting" and progress["total"] == 0 and progress["bytes"] == 0:
                        continue
                    # Include if not finished, or finished very recently (< 5 seconds ago)
                    if (progress["percent"] < 100 or
                            (current_time - progress["last_update"]) < 5.0):
                        active_downloads.append(progress.copy())

                # Store all active downloads for the UI to display
                download_tasks[task_id]["active_downloads"] = active_downloads
            return progress_update

        progress_update_fn = create_progress_update()

        def download_task():
            try:
                download_tasks[task_id]["status"] = "running"
                download_tasks[task_id]["stage"] = "resolving"
                download_tasks[task_id]["message"] = "Resolving tiles and searching for items..."

                if has_tiles:
                    download_tasks[task_id]["details"]["tiles_found"] = len(tiles)
                    result = resolver.resolve_tiles(
                        tiles,
                        limit=limit,
                        force=force,
                        progress_cb=progress_callback,
                        progress_update_cb=progress_update_fn,
                    )
                elif has_roi:
                    download_tasks[task_id]["stage"] = "computing_tiles"
                    download_tasks[task_id]["message"] = "Computing tiles for ROI..."
                    result = resolver.resolve_roi(
                        tuple(roi),
                        limit=limit,
                        force=force,
                        progress_cb=progress_callback,
                        progress_update_cb=progress_update_fn,
                    )
                    download_tasks[task_id]["details"]["tiles_found"] = len(result.mgrs_tiles)
                elif has_region:
                    download_tasks[task_id]["stage"] = "computing_tiles"
                    download_tasks[task_id]["message"] = f"Computing tiles for region: {region}..."
                    result = resolver.resolve_region(
                        region,
                        limit=limit,
                        force=force,
                        progress_cb=progress_callback,
                        progress_update_cb=progress_update_fn,
                    )
                    download_tasks[task_id]["details"]["tiles_found"] = len(result.mgrs_tiles)
                else:
                    raise ValueError("No valid input provided")

                download_tasks[task_id]["stage"] = "downloading"
                download_tasks[task_id]["message"] = "Downloading images..."

                # Wait a bit for final progress updates
                import time
                time.sleep(0.5)

                # Reload cache to include newly downloaded items
                cache.reload()

                # Clear active downloads to remove any "extracting" or finished downloads
                download_tasks[task_id]["active_downloads"] = []

                download_tasks[task_id]["status"] = "completed"
                download_tasks[task_id]["stage"] = "completed"
                download_tasks[task_id]["message"] = "Download completed successfully"
                download_tasks[task_id]["progress"] = 100
                download_tasks[task_id]["result"] = {
                    "downloaded_items": result.downloaded_items,
                    "failed_items": result.failed_items,
                    "downloaded_files": result.downloaded_files,
                    "failed_files": result.failed_files,
                    "unresolved_tiles": result.unresolved_tiles,
                    "mgrs_tiles": result.mgrs_tiles,
                }
                # Update final counts (use result values as they are authoritative)
                # The progress callback may have counted some items, but the final result
                # is the source of truth, so we use it to ensure accuracy
                download_tasks[task_id]["details"]["items_downloaded"] = result.downloaded_items
                download_tasks[task_id]["details"]["items_failed"] = result.failed_items
            except Exception as exc:
                logger.error(f"Download task {task_id} failed: {exc}")
                download_tasks[task_id]["status"] = "error"
                download_tasks[task_id]["stage"] = "error"
                download_tasks[task_id]["error"] = str(exc)
                download_tasks[task_id]["message"] = f"Error: {exc}"

        background_tasks.add_task(download_task)

        return {
            "task_id": task_id,
            "status": "started",
        }

    @app.get("/api/tasks/{task_id}")
    async def get_task_status(task_id: str):
        """Get status of a download task."""
        task = download_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return task

    @app.post("/api/tiles/{tile_code}/images/{item_id}/rate")
    async def rate_image(tile_code: str, item_id: str, request: Dict[str, Any]):
        """Rate an image."""
        rating = request.get("rating")
        if rating is None:
            raise HTTPException(status_code=400, detail="rating is required")

        try:
            rating_float = float(rating)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="rating must be a number")

        # Allow 0 as a valid rating (0.0 to 5.0 inclusive)
        if rating_float < 0 or rating_float > 5:
            raise HTTPException(status_code=400, detail="rating must be between 0.0 and 5.0")

        success = cache.rate_item(item_id, rating_float)
        if not success:
            raise HTTPException(status_code=404, detail=f"Image {item_id} not found")

        return {"success": True, "item_id": item_id, "rating": rating_float}

    @app.delete("/api/tiles/{tile_code}/images/{item_id}")
    async def delete_image(tile_code: str, item_id: str):
        """Delete an image from cache."""
        # Reload cache to ensure we have latest data
        cache.reload()
        deleted_path = cache.delete_item(item_id)
        if deleted_path is None:
            raise HTTPException(status_code=404, detail=f"Image {item_id} not found")

        return {"success": True, "deleted_path": deleted_path, "item_id": item_id}

    @app.delete("/api/tiles/{tile_code}")
    async def delete_tile(tile_code: str):
        """Delete all images for a tile from cache."""
        # Reload cache to ensure we have latest data
        cache.reload()
        result = cache.delete_tile(tile_code)

        if result["deleted_count"] == 0:
            raise HTTPException(status_code=404, detail=f"Tile {tile_code} not found in cache")

        return {
            "success": True,
            "tile_code": tile_code,
            "deleted_count": result["deleted_count"],
            "deleted_files": result["deleted_files"],
            "failed_files": result["failed_files"],
        }

    return app
