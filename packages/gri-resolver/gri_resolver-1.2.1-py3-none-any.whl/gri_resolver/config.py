from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResolverConfig:
    gri_base_url: str = os.environ.get(
        "GRI_BASE_URL",
        "https://s3.eu-central-2.wasabisys.com/s2-mpc/catalog",
    )
    gri_collection: str = os.environ.get("GRI_COLLECTION", "GRI_L1C")
    cache_dir: Path = Path(
        os.environ.get(
            "GRI_CACHE_DIR",
            str(Path(__file__).resolve().parent / "cache"),
        )
    ).expanduser()
    output_dir: Path = Path(
        os.environ.get(
            "GRI_OUTPUT_DIR",
            str(Path(__file__).resolve().parent / "outputs"),
        )
    ).expanduser()
    timeout: int = int(os.environ.get("GRI_TIMEOUT", "60"))
    cache_ttl_hours: int = int(os.environ.get("GRI_CACHE_TTL_HOURS", "168"))
    force: bool = os.environ.get("GRI_FORCE", "0") == "1"
    max_workers: int = int(os.environ.get("GRI_MAX_WORKERS", "4"))
    quality_selection_enabled: bool = os.environ.get("GRI_QUALITY_SELECTION", "1") == "1"
    keep_multiple_per_tile: bool = os.environ.get("GRI_KEEP_MULTIPLE_PER_TILE", "1") == "1"
    prefer_recent: bool = os.environ.get("GRI_PREFER_RECENT", "0") == "1"

    def ensure_dirs(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
