"""Deterministic index health scoring for ETF research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from src.etf_research.schemas import IndexHealthScore, ScoreComponent


MIN_REQUIRED_BARS = 20


@dataclass(frozen=True)
class ScoreWeights:
    trend: float = 25
    momentum: float = 20
    relative_strength: float = 20
    volume: float = 10
    volatility: float = 10
    drawdown: float = 10
    breadth: float = 5


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _linear_score(value: float, low: float, high: float, weight: float) -> float:
    if high == low:
        return 0.0
    return _clamp((value - low) / (high - low), 0.0, 1.0) * weight


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


def _return_over(data: pd.DataFrame, days: int) -> Optional[float]:
    if len(data) <= days:
        return None
    start = float(data["close"].iloc[-days - 1])
    end = float(data["close"].iloc[-1])
    if start <= 0:
        return None
    return (end / start - 1) * 100


def _score_trend(data: pd.DataFrame, weight: float) -> ScoreComponent:
    close = data["close"]
    latest = float(close.iloc[-1])
    ma5 = float(close.rolling(5).mean().iloc[-1])
    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma60 = float(close.rolling(60).mean().iloc[-1]) if len(close) >= 60 else None
    ma20_prev = float(close.rolling(20).mean().iloc[-6]) if len(close) >= 25 else ma20

    points = 0.0
    reasons = []
    if latest > ma20:
        points += 0.35
        reasons.append("close_above_ma20")
    if ma5 > ma20:
        points += 0.3
        reasons.append("ma5_above_ma20")
    if ma20 > ma20_prev:
        points += 0.2
        reasons.append("ma20_rising")
    if ma60 is not None and latest > ma60:
        points += 0.15
        reasons.append("close_above_ma60")
    elif ma60 is None:
        points += 0.075
        reasons.append("ma60_unavailable_partial_credit")

    score = round(_clamp(points, 0.0, 1.0) * weight, 2)
    return ScoreComponent("trend", score, weight, ",".join(reasons) or "trend_conditions_not_met")


def _score_momentum(data: pd.DataFrame, weight: float) -> ScoreComponent:
    ret5 = _return_over(data, 5) or 0.0
    ret20 = _return_over(data, 20) or ret5
    normalized = 0.4 * _linear_score(ret5, -3, 5, 1) + 0.6 * _linear_score(ret20, -8, 12, 1)
    score = round(normalized * weight, 2)
    return ScoreComponent("momentum", score, weight, f"ret5={ret5:.2f}%,ret20={ret20:.2f}%")


def _score_relative_strength(
    data: pd.DataFrame,
    benchmark_bars: Optional[pd.DataFrame],
    weight: float,
) -> ScoreComponent:
    if benchmark_bars is None or benchmark_bars.empty:
        return ScoreComponent("relative_strength", None, weight, "benchmark_unavailable", available=False)

    benchmark = _clean_bars(benchmark_bars)
    index_ret = _return_over(data, 20)
    benchmark_ret = _return_over(benchmark, 20)
    if index_ret is None or benchmark_ret is None:
        return ScoreComponent("relative_strength", None, weight, "insufficient_benchmark_history", available=False)

    spread = index_ret - benchmark_ret
    score = round(_linear_score(spread, -8, 8, weight), 2)
    return ScoreComponent("relative_strength", score, weight, f"20d_spread={spread:.2f}%")


def _score_volume(data: pd.DataFrame, weight: float) -> ScoreComponent:
    volume_column = "amount" if "amount" in data.columns else "volume" if "volume" in data.columns else ""
    if not volume_column:
        return ScoreComponent("volume", None, weight, "volume_or_amount_unavailable", available=False)

    series = pd.to_numeric(data[volume_column], errors="coerce").dropna()
    if len(series) < 20:
        return ScoreComponent("volume", None, weight, "insufficient_volume_history", available=False)

    latest = float(series.iloc[-1])
    avg20 = float(series.iloc[-20:].mean())
    if avg20 <= 0:
        return ScoreComponent("volume", None, weight, "invalid_volume_average", available=False)

    ratio = latest / avg20
    score = round(_linear_score(ratio, 0.6, 1.8, weight), 2)
    return ScoreComponent("volume", score, weight, f"{volume_column}_ratio={ratio:.2f}")


def _score_volatility(data: pd.DataFrame, weight: float) -> ScoreComponent:
    returns = data["close"].pct_change().dropna().iloc[-20:] * 100
    if len(returns) < 10:
        return ScoreComponent("volatility", None, weight, "insufficient_return_history", available=False)
    daily_vol = float(returns.std())
    score = round(weight - _linear_score(daily_vol, 1.0, 5.0, weight), 2)
    return ScoreComponent("volatility", score, weight, f"daily_vol_20d={daily_vol:.2f}%")


def _score_drawdown(data: pd.DataFrame, weight: float) -> ScoreComponent:
    window = data["close"].iloc[-60:] if len(data) >= 60 else data["close"]
    recent_high = float(window.max())
    latest = float(window.iloc[-1])
    if recent_high <= 0:
        return ScoreComponent("drawdown", None, weight, "invalid_recent_high", available=False)
    drawdown = (latest / recent_high - 1) * 100
    score = round(weight - _linear_score(abs(drawdown), 0, 20, weight), 2)
    return ScoreComponent("drawdown", score, weight, f"drawdown={drawdown:.2f}%")


def _score_breadth(breadth_up_ratio: Optional[float], weight: float) -> ScoreComponent:
    if breadth_up_ratio is None:
        return ScoreComponent("breadth", None, weight, "breadth_unavailable", available=False)
    ratio = _clamp(float(breadth_up_ratio), 0.0, 1.0)
    score = round(ratio * weight, 2)
    return ScoreComponent("breadth", score, weight, f"up_ratio={ratio:.2f}")


def calculate_index_health_score(
    *,
    index_code: str,
    index_name: str,
    bars: pd.DataFrame,
    benchmark_bars: Optional[pd.DataFrame] = None,
    breadth_up_ratio: Optional[float] = None,
    weights: ScoreWeights = ScoreWeights(),
) -> IndexHealthScore:
    """Calculate a deterministic 0-100 index health score.

    Missing optional components are marked in data_quality and excluded from
    the denominator, so unavailable breadth or benchmark data does not silently
    become a bearish signal.
    """
    data = _clean_bars(bars)
    components: Dict[str, ScoreComponent] = {
        "trend": _score_trend(data, weights.trend),
        "momentum": _score_momentum(data, weights.momentum),
        "relative_strength": _score_relative_strength(data, benchmark_bars, weights.relative_strength),
        "volume": _score_volume(data, weights.volume),
        "volatility": _score_volatility(data, weights.volatility),
        "drawdown": _score_drawdown(data, weights.drawdown),
        "breadth": _score_breadth(breadth_up_ratio, weights.breadth),
    }

    available_weight = sum(component.weight for component in components.values() if component.available)
    raw_score = sum(component.score or 0 for component in components.values() if component.available)
    adjusted_score = int(round(raw_score * 100 / available_weight)) if available_weight else 0
    data_quality = {
        key: component.detail
        for key, component in components.items()
        if not component.available
    }

    return IndexHealthScore(
        index_code=index_code,
        index_name=index_name,
        score=int(_clamp(adjusted_score, 0, 100)),
        components=components,
        data_quality=data_quality,
    )
