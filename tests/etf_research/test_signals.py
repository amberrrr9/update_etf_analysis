from __future__ import annotations

import pandas as pd
import pytest

from src.etf_research.signals import discover_industry_clue


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


def test_discover_industry_clue_outputs_trigger_evidence_without_score():
    index_bars = _bars(100, 3)
    benchmark_bars = _bars(100, 0.1)

    result = discover_industry_clue(
        index_code="H30184",
        index_name="中证半导体产业指数",
        bars=index_bars,
        benchmark_bars=benchmark_bars,
        breadth_up_ratio=0.72,
        source="unit-test",
    )

    payload = result.to_dict()
    metrics = {item.metric for item in result.trigger_evidence}

    assert "score" not in payload
    assert "weekly_return_pct" in metrics
    assert "weekly_relative_strength_pct" in metrics
    assert "constituent_up_ratio" in metrics
    assert "focus_eligibility" not in result.data_quality


def test_discover_industry_clue_marks_optional_inputs_unavailable():
    result = discover_industry_clue(
        index_code="000300",
        index_name="沪深300",
        bars=_bars(100, 0.05).drop(columns=["amount"]),
    )

    assert result.data_quality["turnover"] == "amount_or_volume_unavailable"
    assert result.data_quality["relative_strength"] == "benchmark_unavailable"
    assert result.data_quality["breadth"] == "breadth_unavailable"
    assert "focus_eligibility" in result.data_quality


def test_discover_industry_clue_requires_close_history():
    with pytest.raises(ValueError, match="at least 20"):
        discover_industry_clue(
            index_code="SHORT",
            index_name="Short History",
            bars=pd.DataFrame({"close": [1, 2, 3]}),
        )
