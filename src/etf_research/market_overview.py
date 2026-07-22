"""AkShare-backed market overview for the ETF research homepage."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List, Optional, Sequence

import pandas as pd

from src.etf_research.schemas import EtfMarketOverview, MarketIndexSnapshot, MarketOverviewItem


INDEX_WATCHLIST = (
    ("000001", "上证指数"),
    ("399001", "深证成指"),
    ("000300", "沪深300"),
    ("000905", "中证500"),
    ("399006", "创业板指"),
    ("000688", "科创50"),
)


def _first_existing_column(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    text = str(value).replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "--", "None", "nan"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _format_pct(value: Optional[float]) -> str:
    if value is None:
        return "--"
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


def _format_amount_yi(value: Optional[float]) -> str:
    if value is None:
        return "--"
    # East Money usually returns amount in yuan. If a provider already returns
    # an abbreviated value, keep the output readable rather than pretending
    # precision we do not have.
    if abs(value) >= 100_000_000:
        return f"{value / 100_000_000:.0f} 亿"
    if abs(value) >= 10_000:
        return f"{value / 10_000:.0f} 万"
    return f"{value:.0f}"


def _tone(change_pct: Optional[float]) -> str:
    if change_pct is None or change_pct == 0:
        return "flat"
    return "up" if change_pct > 0 else "down"


def _rows_by_code(df: pd.DataFrame, code_column: str) -> dict[str, pd.Series]:
    rows: dict[str, pd.Series] = {}
    for _, row in df.iterrows():
        code = str(row.get(code_column, "")).strip()
        if code:
            rows[code] = row
    return rows


def _build_index_snapshots(index_df: pd.DataFrame) -> List[MarketIndexSnapshot]:
    code_column = _first_existing_column(index_df, ("代码", "指数代码", "symbol", "code"))
    name_column = _first_existing_column(index_df, ("名称", "指数名称", "name"))
    change_column = _first_existing_column(index_df, ("涨跌幅", "涨跌幅%", "change_pct", "pct_chg"))
    amount_column = _first_existing_column(index_df, ("成交额", "成交金额", "amount"))

    if not code_column:
        return []

    by_code = _rows_by_code(index_df, code_column)
    snapshots: List[MarketIndexSnapshot] = []
    for code, fallback_name in INDEX_WATCHLIST:
        row = by_code.get(code)
        if row is None:
            continue
        name = str(row.get(name_column, fallback_name)).strip() if name_column else fallback_name
        change_pct = _safe_float(row.get(change_column)) if change_column else None
        amount = _safe_float(row.get(amount_column)) if amount_column else None
        snapshots.append(
            MarketIndexSnapshot(
                name=name or fallback_name,
                code=code,
                change=_format_pct(change_pct),
                turnover=_format_amount_yi(amount),
                tone=_tone(change_pct),
            )
        )
    return snapshots


def _count_positive(values: Iterable[Any]) -> tuple[int, int]:
    total = 0
    positive = 0
    for value in values:
        number = _safe_float(value)
        if number is None:
            continue
        total += 1
        if number > 0:
            positive += 1
    return positive, total


def _sum_amount(df: pd.DataFrame, columns: Sequence[str]) -> Optional[float]:
    amount_column = _first_existing_column(df, columns)
    if not amount_column:
        return None
    values = [_safe_float(value) for value in df[amount_column].tolist()]
    clean_values = [value for value in values if value is not None]
    if not clean_values:
        return None
    return float(sum(clean_values))


def _strong_style(index_snapshots: Sequence[MarketIndexSnapshot]) -> str:
    growth_names = {"创业板指", "科创50"}
    broad_names = {"沪深300", "中证500", "上证指数", "深证成指"}

    def pct(item: MarketIndexSnapshot) -> Optional[float]:
        return _safe_float(item.change)

    growth_values = [pct(item) for item in index_snapshots if item.name in growth_names]
    broad_values = [pct(item) for item in index_snapshots if item.name in broad_names]
    growth_values = [value for value in growth_values if value is not None]
    broad_values = [value for value in broad_values if value is not None]
    if not growth_values or not broad_values:
        return "待观察"
    return "成长" if sum(growth_values) / len(growth_values) >= sum(broad_values) / len(broad_values) else "宽基"


def _risk_temperature(index_snapshots: Sequence[MarketIndexSnapshot], industry_positive: int, industry_total: int) -> str:
    index_changes = [_safe_float(item.change) for item in index_snapshots]
    clean_changes = [value for value in index_changes if value is not None]
    avg_change = sum(clean_changes) / len(clean_changes) if clean_changes else 0
    breadth = industry_positive / industry_total if industry_total else 0
    if avg_change > 0.6 and breadth >= 0.6:
        return "偏暖"
    if avg_change < -0.6 or breadth < 0.35:
        return "偏冷"
    return "中性"


def build_market_overview() -> EtfMarketOverview:
    """Fetch and summarize the A-share ETF market overview via AkShare."""

    errors: List[str] = []
    try:
        import akshare as ak
    except Exception as exc:  # noqa: BLE001 - keep API usable without optional dependency.
        raise RuntimeError("AkShare is not installed or cannot be imported") from exc

    data_date = datetime.now().date().isoformat()

    try:
        index_df = ak.stock_zh_index_spot_em()
    except Exception as exc:  # noqa: BLE001 - data source errors are surfaced.
        index_df = pd.DataFrame()
        errors.append(f"指数行情获取失败: {exc}")

    try:
        etf_df = ak.fund_etf_spot_em()
    except Exception as exc:  # noqa: BLE001
        etf_df = pd.DataFrame()
        errors.append(f"ETF 行情获取失败: {exc}")

    try:
        industry_df = ak.stock_board_industry_name_em()
    except Exception as exc:  # noqa: BLE001
        industry_df = pd.DataFrame()
        errors.append(f"行业板块获取失败: {exc}")

    index_snapshots = _build_index_snapshots(index_df) if not index_df.empty else []
    industry_change_column = _first_existing_column(industry_df, ("涨跌幅", "涨跌幅%", "change_pct", "pct_chg"))
    industry_positive, industry_total = (
        _count_positive(industry_df[industry_change_column].tolist())
        if (not industry_df.empty and industry_change_column)
        else (0, 0)
    )
    etf_amount = _sum_amount(etf_df, ("成交额", "成交金额", "amount")) if not etf_df.empty else None
    strong_style = _strong_style(index_snapshots)
    risk_temperature = _risk_temperature(index_snapshots, industry_positive, industry_total)

    overview = [
        MarketOverviewItem(
            label="上涨行业",
            value=f"{industry_positive} / {industry_total}" if industry_total else "--",
            note="行业扩散度偏积极" if industry_total and industry_positive / industry_total >= 0.5 else "行业扩散度待观察",
        ),
        MarketOverviewItem(
            label="ETF 成交额",
            value=_format_amount_yi(etf_amount),
            note="A 股场内 ETF 实时成交额合计" if etf_amount else "ETF 成交额暂不可用",
        ),
        MarketOverviewItem(
            label="强势风格",
            value=strong_style,
            note="基于创业板/科创与主要宽基相对表现",
        ),
        MarketOverviewItem(
            label="风险温度",
            value=risk_temperature,
            note="由主要指数涨跌和行业扩散度估算",
        ),
    ]

    if index_snapshots:
        summary = (
            f"AkShare 已返回 {len(index_snapshots)} 个主要指数，"
            f"行业上涨 {industry_positive}/{industry_total}，ETF 成交额约 {_format_amount_yi(etf_amount)}。"
        )
    else:
        summary = "AkShare 暂未返回可用主要指数数据，页面应继续使用前端样例数据。"

    return EtfMarketOverview(
        data_date=data_date,
        source="akshare",
        market_indices=index_snapshots,
        overview=overview,
        summary=summary,
        errors=errors,
    )
