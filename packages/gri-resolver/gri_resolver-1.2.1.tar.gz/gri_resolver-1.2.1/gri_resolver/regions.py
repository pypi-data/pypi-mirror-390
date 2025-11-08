from __future__ import annotations

from typing import Dict, List, Optional


PREDEFINED_REGIONS: Dict[str, Dict[str, object]] = {
    "gabon": {
        "name": "Gabon",
        "bounds": [8.5, -4.0, 14.5, 2.3],
        "description": "Republic of Gabon",
    },
    "france": {
        "name": "Metropolitan France",
        "bounds": [-5.0, 41.0, 10.0, 51.0],
        "description": "Metropolitan France",
    },
    "senegal": {
        "name": "Senegal",
        "bounds": [-18.0, 12.0, -11.0, 17.0],
        "description": "Republic of Senegal",
    },
    "cote_ivoire": {
        "name": "Ivory Coast",
        "bounds": [-8.5, 4.0, -2.5, 11.0],
        "description": "Republic of Ivory Coast",
    },
    "mali": {
        "name": "Mali",
        "bounds": [-12.0, 10.0, 4.0, 25.0],
        "description": "Republic of Mali",
    },
    "burkina_faso": {
        "name": "Burkina Faso",
        "bounds": [-5.5, 9.0, 2.5, 15.0],
        "description": "Burkina Faso",
    },
    "niger": {
        "name": "Niger",
        "bounds": [0.0, 11.0, 16.0, 24.0],
        "description": "Republic of Niger",
    },
    "tchad": {
        "name": "Tchad",
        "bounds": [13.0, 7.0, 24.0, 24.0],
        "description": "Republic of Chad",
    },
    "cameroun": {
        "name": "Cameroun",
        "bounds": [8.0, 1.0, 16.0, 13.0],
        "description": "Republic of Cameroun",
    },
    "rca": {
        "name": "Republic of Central Africa",
        "bounds": [14.0, 2.0, 27.0, 11.0],
        "description": "Republic of Central Africa",
    },
    "rdc": {
        "name": "Democratic Republic of the Congo",
        "bounds": [12.0, -14.0, 32.0, 6.0],
        "description": "Democratic Republic of the Congo",
    },
    "congo": {
        "name": "Republic of Congo",
        "bounds": [11.0, -5.0, 19.0, 4.0],
        "description": "Republic of Congo",
    },
    # --- Europe (EU27 + UK + EFTA) quick bounding boxes ---
    "austria": {"name": "Austria", "bounds": [9.5, 46.4, 17.2, 49.0], "description": "Austria"},
    "belgium": {"name": "Belgium", "bounds": [2.5, 49.5, 6.4, 51.5], "description": "Belgium"},
    "bulgaria": {"name": "Bulgaria", "bounds": [22.3, 41.2, 28.6, 44.2], "description": "Bulgaria"},
    "croatia": {"name": "Croatia", "bounds": [13.5, 42.3, 19.4, 46.9], "description": "Croatia"},
    "cyprus": {"name": "Cyprus", "bounds": [32.0, 34.5, 34.9, 35.9], "description": "Cyprus"},
    "czechia": {"name": "Czechia", "bounds": [12.0, 48.5, 18.9, 51.1], "description": "Czech Republic"},
    "denmark": {"name": "Denmark", "bounds": [8.0, 54.5, 15.5, 57.8], "description": "Denmark"},
    "estonia": {"name": "Estonia", "bounds": [21.5, 57.3, 28.2, 59.7], "description": "Estonia"},
    "finland": {"name": "Finland", "bounds": [20.5, 59.5, 31.6, 70.2], "description": "Finland"},
    "germany": {"name": "Germany", "bounds": [5.9, 47.2, 15.1, 55.1], "description": "Germany"},
    "greece": {"name": "Greece", "bounds": [19.3, 34.8, 29.7, 41.8], "description": "Greece"},
    "hungary": {"name": "Hungary", "bounds": [16.1, 45.7, 22.9, 48.6], "description": "Hungary"},
    "ireland": {"name": "Ireland", "bounds": [-10.8, 51.3, -5.4, 55.5], "description": "Ireland"},
    "italy": {"name": "Italy", "bounds": [6.6, 36.6, 18.6, 47.1], "description": "Italy"},
    "latvia": {"name": "Latvia", "bounds": [20.9, 55.7, 28.3, 58.1], "description": "Latvia"},
    "lithuania": {"name": "Lithuania", "bounds": [21.0, 53.9, 26.8, 56.4], "description": "Lithuania"},
    "luxembourg": {"name": "Luxembourg", "bounds": [5.7, 49.4, 6.5, 50.2], "description": "Luxembourg"},
    "malta": {"name": "Malta", "bounds": [14.1, 35.6, 14.7, 36.1], "description": "Malta"},
    "netherlands": {"name": "Netherlands", "bounds": [3.3, 50.7, 7.2, 53.7], "description": "Netherlands"},
    "poland": {"name": "Poland", "bounds": [14.1, 49.0, 24.2, 54.8], "description": "Poland"},
    "portugal": {"name": "Portugal", "bounds": [-9.6, 36.8, -6.2, 42.2], "description": "Portugal (continental)"},
    "romania": {"name": "Romania", "bounds": [20.3, 43.6, 29.7, 48.3], "description": "Romania"},
    "slovakia": {"name": "Slovakia", "bounds": [16.8, 47.7, 22.6, 49.6], "description": "Slovakia"},
    "slovenia": {"name": "Slovenia", "bounds": [13.4, 45.4, 16.6, 46.9], "description": "Slovenia"},
    "spain": {"name": "Spain", "bounds": [-9.3, 36.0, 3.3, 43.8], "description": "Spain (continental)"},
    "sweden": {"name": "Sweden", "bounds": [11.1, 55.2, 24.2, 69.1], "description": "Sweden"},
    # UK + EFTA
    "united_kingdom": {"name": "United Kingdom", "bounds": [-8.6, 49.9, 1.8, 58.7], "description": "United Kingdom"},
    "norway": {"name": "Norway", "bounds": [4.5, 57.9, 31.1, 71.3], "description": "Norway (mainland)"},
    "switzerland": {"name": "Switzerland", "bounds": [5.9, 45.8, 10.5, 47.9], "description": "Switzerland"},
    "iceland": {"name": "Iceland", "bounds": [-24.7, 63.1, -13.2, 66.7], "description": "Iceland"},
    "liechtenstein": {"name": "Liechtenstein", "bounds": [9.45, 47.05, 9.64, 47.28], "description": "Liechtenstein"},
}


def get_region_bounds(region: str) -> Optional[List[float]]:
    r = PREDEFINED_REGIONS.get(region.lower())
    if r:
        return list(r["bounds"])  # type: ignore[index]
    return None
