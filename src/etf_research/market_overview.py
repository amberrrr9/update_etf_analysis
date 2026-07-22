"""AkShare-backed market overview for the ETF research homepage."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterable, List, Optional, Sequence

import pandas as pd

from src.etf_research.schemas import EtfMarketOverview, MarketIndexSnapshot, MarketOverviewItem


INDEX_WATCHLIST = (
    ("000001", "上证指数", "sh000001", "sh000001"),
    ("399001", "深证成指", "sz399001", "sz399001"),
    ("000300", "沪深300", "sh000300", "sh000300"),
    ("000905", "中证500", "sh000905", "sh000905"),
    ("399006", "创业板指", "sz399006", "sz399006"),
    ("000688", "科创50", "sh000688", "sh000688"),
)

PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


@contextmanager
def _without_proxy_env():
    """Run AkShare calls without inheriting broken local proxy variables."""

    previous_values = {key: os.environ.get(key) for key in PROXY_ENV_KEYS}
    previous_no_proxy = {key: os.environ.get(key) for key in ("NO_PROXY", "no_proxy")}
    try:
        for key in PROXY_ENV_KEYS:
            os.environ.pop(key, None)
        os.environ["NO_PROXY"] = "*"
        os.environ["no_proxy"] = "*"
        yield
    finally:
        for key, value in previous_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        for key, value in previous_no_proxy.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


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


def _normalize_index_code(value: Any) -> str:
    text = str(value or "").strip().lower()
    for prefix in ("sh", "sz", "csi"):
        if text.startswith(prefix):
            return text[len(prefix) :]
    return text


def _build_index_snapshots(index_df: pd.DataFrame) -> List[MarketIndexSnapshot]:
    code_column = _first_existing_column(index_df, ("代码", "指数代码", "symbol", "code"))
    name_column = _first_existing_column(index_df, ("名称", "指数名称", "name"))
    change_column = _first_existing_column(index_df, ("涨跌幅", "涨跌幅%", "change_pct", "pct_chg"))
    amount_column = _first_existing_column(index_df, ("成交额", "成交金额", "amount"))

    if not code_column:
        return []

    by_code = {}
    for _, row in index_df.iterrows():
        normalized_code = _normalize_index_code(row.get(code_column))
        if normalized_code:
            by_code[normalized_code] = row

    snapshots: List[MarketIndexSnapshot] = []
    for code, fallback_name, _, _ in INDEX_WATCHLIST:
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


def _build_index_snapshots_from_tx_daily(ak: Any, errors: List[str]) -> List[MarketIndexSnapshot]:
    snapshots: List[MarketIndexSnapshot] = []
    for code, fallback_name, _, tx_symbol in INDEX_WATCHLIST:
        try:
            with _without_proxy_env():
                df = ak.stock_zh_index_daily_tx(symbol=tx_symbol)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{fallback_name} 腾讯日线获取失败: {exc}")
            continue
        if df.empty or len(df) < 2:
            errors.append(f"{fallback_name} 腾讯日线数据不足")
            continue
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        latest_close = _safe_float(latest.get("close"))
        previous_close = _safe_float(previous.get("close"))
        change_pct = (
            ((latest_close - previous_close) / previous_close) * 100
            if latest_close is not None and previous_close not in (None, 0)
            else None
        )
        amount = _safe_float(latest.get("amount"))
        snapshots.append(
            MarketIndexSnapshot(
                name=fallback_name,
                code=code,
                change=_format_pct(change_pct),
                turnover=_format_amount_yi(amount),
                tone=_tone(change_pct),
            )
        )
    return snapshots


def _fetch_index_snapshots(ak: Any, errors: List[str]) -> List[MarketIndexSnapshot]:
    try:
        with _without_proxy_env():
            sina_df = ak.stock_zh_index_spot_sina()
        snapshots = _build_index_snapshots(sina_df)
        if len(snapshots) >= 4:
            return snapshots
        errors.append(f"新浪实时指数只返回 {len(snapshots)} 个主要指数，尝试腾讯日线兜底")
    except Exception as exc:  # noqa: BLE001 - data source errors are surfaced.
        errors.append(f"新浪指数行情获取失败: {exc}")

    snapshots = _build_index_snapshots_from_tx_daily(ak, errors)
    if snapshots:
        return snapshots

    try:
        with _without_proxy_env():
            em_df = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
        return _build_index_snapshots(em_df)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"东方财富指数行情获取失败: {exc}")
        return []


def _fetch_industry_df(ak: Any, errors: List[str]) -> pd.DataFrame:
    try:
        with _without_proxy_env():
            return ak.stock_board_industry_summary_ths()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"同花顺行业概览获取失败: {exc}")

    try:
        with _without_proxy_env():
            return ak.stock_board_industry_name_em()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"东方财富行业板块获取失败: {exc}")
        return pd.DataFrame()


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

    index_snapshots = _fetch_index_snapshots(ak, errors)

    try:
        with _without_proxy_env():
            etf_df = ak.fund_etf_spot_em()
    except Exception as exc:  # noqa: BLE001
        etf_df = pd.DataFrame()
        errors.append(f"ETF 行情获取失败: {exc}")

    industry_df = _fetch_industry_df(ak, errors)

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
        summary = "AkShare 暂未返回可用主要指数数据。"

    return EtfMarketOverview(
        data_date=data_date,
        source="akshare",
        market_indices=index_snapshots,
        overview=overview,
        summary=summary,
        errors=errors,
    )
