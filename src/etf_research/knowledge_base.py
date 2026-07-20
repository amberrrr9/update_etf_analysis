"""Local knowledge-base loaders for ETF research MVP."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from src.etf_research.schemas import ETFMaster, IndexMaster


def load_etf_master(path: str | Path) -> List[ETFMaster]:
    """Load ETF master data from CSV."""
    records: List[ETFMaster] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            records.append(
                ETFMaster(
                    etf_code=(row.get("etf_code") or "").strip(),
                    etf_name=(row.get("etf_name") or "").strip(),
                    exchange=(row.get("exchange") or "").strip(),
                    fund_company=(row.get("fund_company") or "").strip(),
                    tracking_index_code=(row.get("tracking_index_code") or "").strip(),
                    tracking_index_name=(row.get("tracking_index_name") or "").strip(),
                    management_fee=_optional_float(row.get("management_fee")),
                    fund_size=_optional_float(row.get("fund_size")),
                    category_l1=(row.get("category_l1") or "").strip(),
                    category_l2=(row.get("category_l2") or "").strip(),
                    category_l3=(row.get("category_l3") or "").strip(),
                    listed_date=(row.get("listed_date") or "").strip(),
                )
            )
    return records


def load_index_master(path: str | Path) -> List[IndexMaster]:
    """Load index master data from CSV."""
    records: List[IndexMaster] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            records.append(
                IndexMaster(
                    index_code=(row.get("index_code") or "").strip(),
                    index_name=(row.get("index_name") or "").strip(),
                    category_l1=(row.get("category_l1") or "").strip(),
                    category_l2=(row.get("category_l2") or "").strip(),
                    category_l3=(row.get("category_l3") or "").strip(),
                    industry=(row.get("industry") or "").strip(),
                    style=(row.get("style") or "").strip(),
                    weight_rule=(row.get("weight_rule") or "").strip(),
                    rebalance_rule=(row.get("rebalance_rule") or "").strip(),
                )
            )
    return records


def _optional_float(value: object) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None
