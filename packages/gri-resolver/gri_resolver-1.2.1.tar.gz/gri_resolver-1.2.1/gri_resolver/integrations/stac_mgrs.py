#!/usr/bin/env python3
"""
MGRS and UTM/GZD conversion module for STAC interface.
Handles conversion between lat/lon coordinates and MGRS/UTM tile systems.
"""

from __future__ import annotations

import re
from typing import List, Tuple, Optional
import mgrs
import logging


class STACMGRS:
    """MGRS and UTM/GZD conversion manager for STAC interface."""

    def __init__(self):
        """Initialize the MGRS conversion manager."""
        self.mgrs_converter = mgrs.MGRS()
        self.logger = logging.getLogger(__name__)

    def lat_lon_to_mgrs(self, lat: float, lon: float) -> str:
        try:
            mgrs_coords = self.mgrs_converter.toMGRS(lat, lon)
            self.logger.debug(f"Converted ({lat}, {lon}) to MGRS: {mgrs_coords}")
            return mgrs_coords
        except Exception as e:
            self.logger.error(f"Error converting to MGRS: {e}")
            raise

    def mgrs_to_lat_lon(self, mgrs_coords: str) -> Tuple[float, float]:
        try:
            lat, lon = self.mgrs_converter.toLatLon(mgrs_coords)
            self.logger.debug(f"Converted MGRS {mgrs_coords} to ({lat}, {lon})")
            return lat, lon
        except Exception as e:
            self.logger.error(f"Error converting from MGRS: {e}")
            raise

    def extract_mgrs_components(self, mgrs_coords: str) -> dict:
        try:
            pattern = r"^(\d{2})([A-Z])([A-Z]{2})"
            match = re.match(pattern, mgrs_coords)
            if match:
                utm_zone = match.group(1)
                gzd_band = match.group(2)
                square_id = match.group(3)
                return {
                    "utm_zone": utm_zone,
                    "gzd_band": gzd_band,
                    "square_id": square_id,
                    "full_mgrs": mgrs_coords,
                }
            else:
                raise ValueError(f"Invalid MGRS format: {mgrs_coords}")
        except Exception as e:
            self.logger.error(f"Error extracting MGRS components: {e}")
            raise

    def extract_utm_gzd_from_mgrs(self, mgrs_coords: str) -> str:
        try:
            utm_gzd = mgrs_coords[:5]
            if len(utm_gzd) == 5:
                self.logger.debug(
                    f"Extracted UTM/GZD {utm_gzd} from MGRS {mgrs_coords}"
                )
                return utm_gzd
            else:
                raise ValueError(f"Invalid UTM/GZD format: {mgrs_coords}")
        except Exception as e:
            self.logger.error(f"Error extracting UTM/GZD: {e}")
            raise

    def extract_utm_gzd_from_item_id(self, item_id: str) -> Optional[str]:
        try:
            pattern = r"_T(\d{2}[A-Z][A-Z]{2})_"
            match = re.search(pattern, item_id)
            if match:
                utm_gzd = match.group(1)
                self.logger.debug(f"Extracted UTM/GZD {utm_gzd} from item ID {item_id}")
                return utm_gzd
            else:
                self.logger.debug(f"No UTM/GZD found in item ID: {item_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting UTM/GZD from item ID: {e}")
            return None

    def get_mgrs_tiles_from_roi(
        self, roi_bounds: List[float], sample_points: int = 100
    ) -> List[str]:
        try:
            min_lon, min_lat, max_lon, max_lat = roi_bounds
            tiles = set()
            corners = [
                (min_lat, min_lon),
                (min_lat, max_lon),
                (max_lat, min_lon),
                (max_lat, max_lon),
            ]
            for lat, lon in corners:
                try:
                    mgrs_coords = self.lat_lon_to_mgrs(lat, lon)
                    utm_gzd = self.extract_utm_gzd_from_mgrs(mgrs_coords)
                    if utm_gzd and len(utm_gzd) == 5:
                        tiles.add(utm_gzd)
                except Exception as e:
                    self.logger.warning(
                        f"Error converting corner point ({lat}, {lon}): {e}"
                    )
            import random

            for _ in range(sample_points):
                lat = random.uniform(min_lat, max_lat)
                lon = random.uniform(min_lon, max_lon)
                try:
                    mgrs_coords = self.lat_lon_to_mgrs(lat, lon)
                    utm_gzd = self.extract_utm_gzd_from_mgrs(mgrs_coords)
                    if utm_gzd and len(utm_gzd) == 5:
                        tiles.add(utm_gzd)
                except Exception as e:
                    self.logger.warning(
                        f"Error converting sample point ({lat}, {lon}): {e}"
                    )
            tiles_list = list(tiles)
            self.logger.info(
                f"Found {len(tiles_list)} UTM/GZD tiles for ROI: {tiles_list}"
            )
            return tiles_list
        except Exception as e:
            self.logger.error(f"Error getting UTM/GZD tiles from ROI: {e}")
            raise

    def construct_utm_gzd_path(self, utm_gzd: str) -> str:
        try:
            if len(utm_gzd) != 5:
                raise ValueError(f"Invalid UTM/GZD format: {utm_gzd}")
            utm_zone = utm_gzd[:2]
            gzd_band = utm_gzd[2]
            square_id = utm_gzd[3:5]
            path = f"T{utm_zone}/T{utm_zone}{gzd_band}/T{utm_zone}{gzd_band}{square_id}"
            self.logger.debug(f"Constructed path {path} from UTM/GZD {utm_gzd}")
            return path
        except Exception as e:
            self.logger.error(f"Error constructing UTM/GZD path: {e}")
            raise

    def construct_utm_gzd_path_variants(self, utm_gzd: str) -> list[str]:
        """Return common path variants for a given tile id.

        Examples tried (in order):
        - T31/T31U/T31UDQ
        - 31/31U/31UDQ
        - lowercase versions of the above
        """
        if not self.validate_utm_gzd(utm_gzd):
            return []
        zone = utm_gzd[:2]
        band = utm_gzd[2]
        square = utm_gzd[3:5]
        with_t = f"T{zone}/T{zone}{band}/T{zone}{band}{square}"
        without_t = f"{zone}/{zone}{band}/{zone}{band}{square}"
        return [
            with_t,
            without_t,
            with_t.lower(),
            without_t.lower(),
        ]

    def validate_utm_gzd(self, utm_gzd: str) -> bool:
        try:
            if len(utm_gzd) != 5:
                return False
            utm_zone = int(utm_gzd[:2])
            gzd_band = utm_gzd[2]
            square_id = utm_gzd[3:5]
            if utm_zone < 1 or utm_zone > 60:
                return False
            valid_bands = "CDEFGHJKLMNPQRSTUVWX"
            if gzd_band not in valid_bands:
                return False
            if not re.match(r"^[A-Z]{2}$", square_id):
                return False
            return True
        except Exception:
            return False
