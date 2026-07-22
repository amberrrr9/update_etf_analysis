"""Schemas for ETF/index research."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TriggerEvidence:
    """One transparent reason an industry/index deserves research attention."""

    metric: str
    value: Any
    condition: str
    description: str
    data_date: str = ""
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IndustryClue:
    """Research clue for an industry index.

    This is not a score or rating. It only records which deterministic
    conditions were triggered and which optional evidence was unavailable.
    """

    index_code: str
    index_name: str
    trigger_evidence: List[TriggerEvidence]
    data_quality: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_code": self.index_code,
            "index_name": self.index_name,
            "trigger_evidence": [item.to_dict() for item in self.trigger_evidence],
            "data_quality": dict(self.data_quality),
        }


@dataclass(frozen=True)
class ETFMaster:
    """ETF master-data row."""

    etf_code: str
    etf_name: str
    exchange: str
    fund_company: str
    tracking_index_code: str
    tracking_index_name: str
    management_fee: Optional[float] = None
    fund_size: Optional[float] = None
    category_l1: str = ""
    category_l2: str = ""
    category_l3: str = ""
    listed_date: str = ""


@dataclass(frozen=True)
class IndexMaster:
    """Index master-data row."""

    index_code: str
    index_name: str
    category_l1: str
    category_l2: str
    category_l3: str
    industry: str = ""
    style: str = ""
    weight_rule: str = ""
    rebalance_rule: str = ""


@dataclass(frozen=True)
class ETFMapping:
    """Index-to-ETF mapping row."""

    index_code: str
    etf_code: str
    is_primary: bool = False
    liquidity_rank: Optional[int] = None
    fund_size_rank: Optional[int] = None


@dataclass(frozen=True)
class IndustryKnowledge:
    """Knowledge-base entry for an industry or theme."""

    industry_code: str
    industry_name: str
    intro: str = ""
    industry_chain: List[str] = field(default_factory=list)
    macro_drivers: List[str] = field(default_factory=list)
    policy_drivers: List[str] = field(default_factory=list)
    news_keywords: List[str] = field(default_factory=list)
    related_indices: List[str] = field(default_factory=list)
    related_etfs: List[str] = field(default_factory=list)
    major_companies: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MarketIndexSnapshot:
    """Display-ready snapshot for a broad market or style index."""

    name: str
    code: str
    change: str
    turnover: str
    tone: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketOverviewItem:
    """One market-wide observation for the ETF research homepage."""

    label: str
    value: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EtfMarketOverview:
    """AkShare-backed full-market overview for the ETF research homepage."""

    data_date: str
    source: str
    market_indices: List[MarketIndexSnapshot]
    overview: List[MarketOverviewItem]
    summary: str
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_date": self.data_date,
            "source": self.source,
            "market_indices": [item.to_dict() for item in self.market_indices],
            "overview": [item.to_dict() for item in self.overview],
            "summary": self.summary,
            "errors": list(self.errors),
        }
