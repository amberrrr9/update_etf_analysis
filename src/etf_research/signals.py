"""Deterministic industry clue discovery for ETF research.

The signal here means "research clue", not a trading signal. This module
intentionally does not output a score, rating, rank, buy/sell suggestion, or
position advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from src.etf_research.schemas import IndustryClue, TriggerEvidence


MIN_REQUIRED_BARS = 20


@dataclass(frozen=True)
class ClueThresholds:
    """Transparent thresholds for research clue discovery."""

    min_daily_abs_return_pct: float = 2.0
    min_weekly_abs_return_pct: float = 4.0
    min_relative_strength_pct: float = 3.0
    min_turnover_ratio: float = 1.5
    min_breadth_up_ratio: float = 0.65
    min_trigger_count: int = 2


def _clean_bars(bars: pd.DataFrame) -> pd.DataFrame:
    if bars is None or bars.empty:
        raise ValueError("index bars are required")
    if "close" not in bars.columns:
        raise ValueError("index bars must contain a close column")

    data = bars.copy()
    if "date" in data.columns:
        data = data.sort_values("date")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data = data.dropna(subset=["close"])
    if len(data) < MIN_REQUIRED_BARS:
        raise ValueError(f"at least {MIN_REQUIRED_BARS} valid close bars are required")
    return data.reset_index(drop=True)


def _data_date(data: pd.DataFrame) -> str:
    if "date" not in data.columns:
        return ""
    value = data["date"].iloc[-1]
    try:
        return pd.Timestamp(value).date().isoformat()
    except Exception:
        return str(value)


def _return_over(data: pd.DataFrame, days: int) -> Optional[float]:
    if len(data) <= days:
        return None
    start = float(data["close"].iloc[-days - 1])
    end = float(data["close"].iloc[-1])
    if start <= 0:
        return None
    return (end / start - 1) * 100


def _add_abs_return_trigger(
    triggers: List[TriggerEvidence],
    *,
    metric: str,
    value: Optional[float],
    threshold: float,
    data_date: str,
    source: str,
) -> None:
    if value is None or abs(value) < threshold:
        return
    direction = "上涨" if value > 0 else "下跌"
    triggers.append(
        TriggerEvidence(
            metric=metric,
            value=round(value, 2),
            condition=f"abs({metric}) >= {threshold}",
            description=f"{metric} {direction} {abs(value):.2f}%，达到行业线索阈值。",
            data_date=data_date,
            source=source,
        )
    )


def _turnover_ratio(data: pd.DataFrame) -> Optional[float]:
    column = "amount" if "amount" in data.columns else "volume" if "volume" in data.columns else ""
    if not column:
        return None
    series = pd.to_numeric(data[column], errors="coerce").dropna()
    if len(series) < 20:
        return None
    latest = float(series.iloc[-1])
    avg20 = float(series.iloc[-20:].mean())
    if avg20 <= 0:
        return None
    return latest / avg20


def discover_industry_clue(
    *,
    index_code: str,
    index_name: str,
    bars: pd.DataFrame,
    benchmark_bars: Optional[pd.DataFrame] = None,
    breadth_up_ratio: Optional[float] = None,
    thresholds: ClueThresholds = ClueThresholds(),
    source: str = "",
) -> IndustryClue:
    """Discover transparent research clues for an industry index.

    Returns all triggered conditions and data-quality notes. An empty
    trigger_evidence list is valid and means the index should not be forced into
    the daily focus list.
    """
    data = _clean_bars(bars)
    data_date = _data_date(data)
    data_quality: Dict[str, str] = {}
    triggers: List[TriggerEvidence] = []

    daily_return = _return_over(data, 1)
    weekly_return = _return_over(data, 5)
    _add_abs_return_trigger(
        triggers,
        metric="daily_return_pct",
        value=daily_return,
        threshold=thresholds.min_daily_abs_return_pct,
        data_date=data_date,
        source=source,
    )
    _add_abs_return_trigger(
        triggers,
        metric="weekly_return_pct",
        value=weekly_return,
        threshold=thresholds.min_weekly_abs_return_pct,
        data_date=data_date,
        source=source,
    )

    turnover_ratio = _turnover_ratio(data)
    if turnover_ratio is None:
        data_quality["turnover"] = "amount_or_volume_unavailable"
    elif turnover_ratio >= thresholds.min_turnover_ratio:
        triggers.append(
            TriggerEvidence(
                metric="turnover_ratio_20d",
                value=round(turnover_ratio, 2),
                condition=f"turnover_ratio_20d >= {thresholds.min_turnover_ratio}",
                description=f"成交较近 20 日均值放大至 {turnover_ratio:.2f} 倍。",
                data_date=data_date,
                source=source,
            )
        )

    if benchmark_bars is None or benchmark_bars.empty:
        data_quality["relative_strength"] = "benchmark_unavailable"
    else:
        benchmark = _clean_bars(benchmark_bars)
        index_weekly = weekly_return
        benchmark_weekly = _return_over(benchmark, 5)
        if index_weekly is None or benchmark_weekly is None:
            data_quality["relative_strength"] = "insufficient_benchmark_history"
        else:
            spread = index_weekly - benchmark_weekly
            if abs(spread) >= thresholds.min_relative_strength_pct:
                direction = "强于" if spread > 0 else "弱于"
                triggers.append(
                    TriggerEvidence(
                        metric="weekly_relative_strength_pct",
                        value=round(spread, 2),
                        condition=f"abs(weekly_relative_strength_pct) >= {thresholds.min_relative_strength_pct}",
                        description=f"近一周相对宽基基准{direction} {abs(spread):.2f} 个百分点。",
                        data_date=data_date,
                        source=source,
                    )
                )

    if breadth_up_ratio is None:
        data_quality["breadth"] = "breadth_unavailable"
    else:
        ratio = max(0.0, min(1.0, float(breadth_up_ratio)))
        if ratio >= thresholds.min_breadth_up_ratio:
            triggers.append(
                TriggerEvidence(
                    metric="constituent_up_ratio",
                    value=round(ratio, 4),
                    condition=f"constituent_up_ratio >= {thresholds.min_breadth_up_ratio}",
                    description=f"成分股上涨比例为 {ratio:.0%}，显示行业内部具备一定扩散度。",
                    data_date=data_date,
                    source=source,
                )
            )

    if len(triggers) < thresholds.min_trigger_count:
        data_quality["focus_eligibility"] = (
            f"trigger_count {len(triggers)} < required {thresholds.min_trigger_count}"
        )

    return IndustryClue(
        index_code=index_code,
        index_name=index_name,
        trigger_evidence=triggers,
        data_quality=data_quality,
    )
