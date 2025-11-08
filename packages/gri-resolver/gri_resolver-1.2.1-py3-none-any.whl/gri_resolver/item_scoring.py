from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def extract_quality_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    """Extract quality-related metadata from a STAC item.

    Args:
        item: STAC item dictionary

    Returns:
        Dictionary with extracted metadata:
        - cloud_cover: float or None (eo:cloud_cover)
        - sun_azimuth: float or None (view:sun_azimuth)
        - sun_elevation: float or None (view:sun_elevation)
        - datetime: datetime or None (properties.datetime)
        - relative_orbits: str or None (properties.Relative Orbits)
    """
    properties = item.get("properties", {}) or {}
    metadata: Dict[str, Any] = {
        "cloud_cover": None,
        "sun_azimuth": None,
        "sun_elevation": None,
        "datetime": None,
        "relative_orbits": None,
    }

    # Extract eo:cloud_cover
    cloud_cover = properties.get("eo:cloud_cover")
    if cloud_cover is not None:
        try:
            metadata["cloud_cover"] = float(cloud_cover)
        except (ValueError, TypeError):
            pass

    # Extract view extension metadata (sun angles)
    sun_azimuth = properties.get("view:sun_azimuth")
    if sun_azimuth is not None:
        try:
            metadata["sun_azimuth"] = float(sun_azimuth)
        except (ValueError, TypeError):
            pass

    sun_elevation = properties.get("view:sun_elevation")
    if sun_elevation is not None:
        try:
            metadata["sun_elevation"] = float(sun_elevation)
        except (ValueError, TypeError):
            pass

    # Extract datetime
    dt_str = properties.get("datetime")
    if dt_str:
        try:
            # Try ISO format parsing
            if isinstance(dt_str, str):
                # Remove timezone info if present for simpler parsing
                dt_str_clean = dt_str.split("+")[0].split("Z")[0].split(".")[0]
                metadata["datetime"] = datetime.fromisoformat(dt_str_clean)
        except (ValueError, TypeError):
            pass

    # Extract relative orbits (custom property)
    relative_orbits = properties.get("Relative Orbits")
    if relative_orbits:
        metadata["relative_orbits"] = str(relative_orbits)

    return metadata


def score_item_quality(
    item: Dict[str, Any],
    metadata: Dict[str, Any],
    prefer_recent: bool = False,
) -> float:
    """Calculate a quality score for a STAC item.

    Higher score = better quality.

    Scoring factors:
    - Cloud cover: lower is better (0% = best, 100% = worst)
    - Sun elevation: higher is better (more direct sunlight)
    - Date: more recent can be preferred if prefer_recent=True

    Args:
        item: STAC item dictionary
        metadata: Extracted metadata from extract_quality_metadata()
        prefer_recent: If True, prefer more recent items

    Returns:
        Quality score (float, higher is better)
        Default score for items without metadata: 0.1 (low but non-zero)
    """
    score = 0.0

    # Cloud cover: lower is better
    # Score: 100 - cloud_cover (so 0% clouds = 100 points, 100% clouds = 0 points)
    cloud_cover = metadata.get("cloud_cover")
    if cloud_cover is not None:
        cloud_score = max(0.0, 100.0 - cloud_cover)
        score += cloud_score * 0.6  # 60% weight for cloud cover
    else:
        # No cloud cover info: give a moderate score
        score += 50.0 * 0.6

    # Sun elevation: higher is better
    # Normalize to 0-100 scale (assuming typical range 0-90 degrees)
    sun_elevation = metadata.get("sun_elevation")
    if sun_elevation is not None:
        # Normalize: 0° = 0 points, 90° = 100 points
        elevation_score = max(0.0, min(100.0, (sun_elevation / 90.0) * 100.0))
        score += elevation_score * 0.3  # 30% weight for sun elevation
    else:
        # No sun elevation: give moderate score
        score += 50.0 * 0.3

    # Date preference: more recent = slightly better (if enabled)
    if prefer_recent:
        dt = metadata.get("datetime")
        if dt:
            # Calculate days since acquisition (more recent = higher score)
            # Normalize: items from last year get up to 10 points bonus
            now = datetime.now()
            days_ago = (now - dt).days
            if days_ago >= 0:
                # Bonus decreases with age: 10 points for today, 0 for 365+ days ago
                date_bonus = max(0.0, 10.0 * (1.0 - min(1.0, days_ago / 365.0)))
                score += date_bonus * 0.1  # 10% weight for recency

    # If we have no metadata at all, return a low but non-zero score
    # This allows items without metadata to still be downloaded
    if score == 0.0:
        score = 0.1

    return score
