from __future__ import annotations

import tarfile
from pathlib import Path
import uuid
from typing import Dict, List, Optional, Any, Callable

import requests


def download_and_extract_tar(
    url: str,
    output_dir: Path,
    logger,
    progress_cb: Optional[Callable[[str], None]] = None,
    progress_update: Optional[Callable[[str, int, int], None]] = None,
) -> List[Path]:
    """Download and extract all image files from a tar archive.

    Returns:
        List of extracted image file paths (empty list if no images found)
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Unique temp file per download to avoid concurrency conflicts
        tmp_name = f"._tmp_{uuid.uuid4().hex}.tar.gz"
        tmp_tar = output_dir / tmp_name
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", "0"))
            downloaded = 0
            if progress_update and total > 0:
                progress_update("start", 0, total)
            last_reported_pct = -1
            with open(tmp_tar, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        if progress_cb and total > 0 and progress_update is None:
                            downloaded += len(chunk)
                            pct = int(downloaded * 100 / total)
                            if pct >= 5 and pct % 5 == 0 and pct != last_reported_pct:
                                progress_cb(f"download {pct}%")
                                last_reported_pct = pct
                        if progress_update and total > 0:
                            progress_update("bytes", len(chunk), total)
        with tarfile.open(tmp_tar, "r:gz") as tar:
            # Extract all image-like files, but exclude those in QI_DATA directory
            image_targets = []
            for member in tar.getmembers():
                name = member.name.lower()
                # Skip images in QI_DATA directory (not exploitable images)
                # Only extract images from IMG_DATA directory (exploitable images)
                if "/qi_data/" in name or "/qi_data\\" in name or "\\qi_data\\" in name:
                    continue
                if name.endswith((".tif", ".tiff", ".jp2")):
                    image_targets.append(member)

            if not image_targets:
                logger.warning("No image assets found in archive")
                try:
                    tmp_tar.unlink(missing_ok=True)
                except Exception:
                    pass
                return []

            if progress_cb:
                progress_cb(f"extracting {len(image_targets)} image(s)...")
            if progress_update:
                progress_update("stage", 0, 0)

            extracted = []
            for target in image_targets:
                tar.extract(target, path=output_dir)
                extracted_path = output_dir / target.name
                extracted.append(extracted_path)
                logger.debug(f"Extracted image: {extracted_path}")

        try:
            tmp_tar.unlink(missing_ok=True)
        except Exception:
            pass
        return extracted
    except Exception as exc:
        logger.error(f"Download/extract error: {exc}")
        return []


def _select_archive_href_from_item(item: Dict[str, Any], logger) -> Optional[str]:
    assets = (item or {}).get("assets", {}) or {}
    # Priority order: explicit tar.gz/zip, then any archive-like, then image directly
    candidates = []
    for key, meta in assets.items():
        href = (meta or {}).get("href")
        if not href:
            continue
        lower = href.lower()
        ctype = (meta or {}).get("type", "").lower()
        roles = meta.get("roles", []) or []
        score = 0
        if lower.endswith((".tar.gz", ".tgz")) or "tar" in ctype:
            score = 100
        elif lower.endswith(".zip") or "zip" in ctype:
            score = 90
        elif lower.endswith((".tif", ".tiff", ".jp2")):
            score = 50
        if "data" in roles:
            score += 5
        candidates.append((score, href))
    if not candidates:
        logger.warning("No suitable assets found on STAC item")
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def handle_reference_download(
    reference_info: Dict,
    output_dir: Path,
    logger,
    progress_cb: Optional[Callable[[str], None]] = None,
    progress_update: Optional[Callable[[str, int, int], None]] = None,
) -> Optional[Dict[str, Any]]:
    """Download and extract images from a STAC item reference.

    Returns:
        Dictionary with "paths" key containing list of image paths,
        or None if download failed
    """
    item = reference_info.get("stac_item", {})
    href = _select_archive_href_from_item(item, logger)
    if not href:
        return None
    if href.lower().endswith((".tar.gz", ".tgz", ".zip")):
        # current implementation supports tar.gz; zip could be added later
        if href.lower().endswith((".zip",)):
            logger.warning("ZIP extraction not implemented yet")
            return None
        images = download_and_extract_tar(href, output_dir, logger, progress_cb, progress_update)
    else:
        # Direct image download (no extraction)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / Path(href).name
            with requests.get(href, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", "0"))
                downloaded = 0
                if progress_update and total > 0:
                    progress_update("start", 0, total)
                last_reported_pct = -1
                with open(target, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            if progress_cb and total > 0 and progress_update is None:
                                downloaded += len(chunk)
                                pct = int(downloaded * 100 / total)
                                if pct >= 5 and pct % 5 == 0 and pct != last_reported_pct:
                                    progress_cb(f"download {pct}%")
                                    last_reported_pct = pct
                            if progress_update and total > 0:
                                progress_update("bytes", len(chunk), total)
            images = [target]
        except Exception as exc:
            logger.error(f"Direct download error: {exc}")
            images = []
    if not images:
        return None
    return {"paths": [str(img) for img in images]}
