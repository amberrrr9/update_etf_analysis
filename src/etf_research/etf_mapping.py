"""ETF mapping helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from src.etf_research.schemas import ETFMapping


def load_index_etf_mappings(path: str | Path) -> List[ETFMapping]:
    """Load index-to-ETF mappings from a CSV file."""
    rows: List[ETFMapping] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                ETFMapping(
                    index_code=(row.get("index_code") or "").strip(),
                    etf_code=(row.get("etf_code") or "").strip(),
                    is_primary=(row.get("is_primary") or "").strip().lower() in {"1", "true", "yes", "y"},
                    liquidity_rank=_optional_int(row.get("liquidity_rank")),
                    fund_size_rank=_optional_int(row.get("fund_size_rank")),
                )
            )
    return rows


def related_etfs(index_code: str, mappings: Iterable[ETFMapping]) -> List[ETFMapping]:
    """Return ETF mappings for an index, ordered by primary/liquidity/fund size."""
    target = str(index_code or "").strip()
    matched = [mapping for mapping in mappings if mapping.index_code == target]
    return sorted(
        matched,
        key=lambda item: (
            not item.is_primary,
            item.liquidity_rank if item.liquidity_rank is not None else 9999,
            item.fund_size_rank if item.fund_size_rank is not None else 9999,
            item.etf_code,
        ),
    )


def _optional_int(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None
