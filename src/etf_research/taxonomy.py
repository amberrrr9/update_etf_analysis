"""Deterministic ETF/index taxonomy constants."""

from __future__ import annotations

from typing import Dict, Tuple


CATEGORY_L1 = (
    "Broad Market",
    "Industry",
    "Theme",
    "Strategy",
    "Commodity",
    "Bond",
    "Cross-border",
)

CATEGORY_L2 = (
    "Technology",
    "Healthcare",
    "Financial",
    "Manufacturing",
    "Consumption",
    "Resources",
    "Utilities",
    "Broad Market",
    "Fixed Income",
    "Commodity",
)

CATEGORY_L3 = (
    "Semiconductor",
    "AI",
    "Robotics",
    "Innovative Drugs",
    "Gold",
    "Rare Metals",
    "Power Grid",
    "Securities",
    "Banks",
    "Dividend",
)


INDEX_TAXONOMY_SEEDS: Dict[str, Tuple[str, str, str]] = {
    "semiconductor": ("Industry", "Technology", "Semiconductor"),
    "ai": ("Theme", "Technology", "AI"),
    "robotics": ("Theme", "Manufacturing", "Robotics"),
    "innovative_drugs": ("Industry", "Healthcare", "Innovative Drugs"),
    "gold": ("Commodity", "Commodity", "Gold"),
    "rare_metals": ("Industry", "Resources", "Rare Metals"),
    "power_grid": ("Industry", "Utilities", "Power Grid"),
    "securities": ("Industry", "Financial", "Securities"),
    "banks": ("Industry", "Financial", "Banks"),
    "dividend": ("Strategy", "Broad Market", "Dividend"),
}


def normalize_taxonomy_key(value: str) -> str:
    """Normalize a human-entered taxonomy key for deterministic lookup."""
    return "_".join(str(value or "").strip().lower().replace("-", " ").split())
