from __future__ import annotations

import pandas as pd
import pytest

from src.etf_research.scoring import calculate_index_health_score


def _bars(start: float, step: float, days: int = 80, amount: float = 100.0) -> pd.DataFrame:
    close = [start + step * i for i in range(days)]
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=days, freq="D"),
            "open": close,
            "high": [value * 1.01 for value in close],
            "low": [value * 0.99 for value in close],
            "close": close,
            "amount": [amount + i for i in range(days)],
        }
    )


def test_calculate_index_health_score_rewards_strong_index_vs_benchmark():
    index_bars = _bars(100, 1.2)
    benchmark_bars = _bars(100, 0.25)

    result = calculate_index_health_score(
        index_code="H30184",
        index_name="中证半导体产业指数",
        bars=index_bars,
        benchmark_bars=benchmark_bars,
        breadth_up_ratio=0.72,
    )

    assert result.score >= 70
    assert result.components["trend"].available is True
    assert result.components["relative_strength"].score is not None
    assert result.components["breadth"].score == pytest.approx(3.6)
    assert result.data_quality == {}


def test_calculate_index_health_score_marks_optional_inputs_unavailable():
    index_bars = _bars(100, 0.2)

    result = calculate_index_health_score(
        index_code="000300",
        index_name="沪深300",
        bars=index_bars.drop(columns=["amount"]),
    )

    assert 0 <= result.score <= 100
    assert result.components["relative_strength"].available is False
    assert result.components["breadth"].available is False
    assert result.components["volume"].available is False
    assert result.data_quality["relative_strength"] == "benchmark_unavailable"
    assert result.data_quality["breadth"] == "breadth_unavailable"


def test_calculate_index_health_score_requires_close_history():
    with pytest.raises(ValueError, match="at least 20"):
        calculate_index_health_score(
            index_code="SHORT",
            index_name="Short History",
            bars=pd.DataFrame({"close": [1, 2, 3]}),
        )
