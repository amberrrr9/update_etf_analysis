"""Schemas for ETF/index research.

The first ETF research MVP uses lightweight dataclasses instead of extending
the existing stock-oriented AnalysisResult. This keeps the new domain separate
from buy/sell decision reports.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ScoreComponent:
    """One deterministic component of an index health score."""

    name: str
    score: Optional[float]
    weight: float
    detail: str
    available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IndexHealthScore:
    """Rule-based health score for an index research object."""

    index_code: str
    index_name: str
    score: int
    components: Dict[str, ScoreComponent]
    data_quality: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_code": self.index_code,
            "index_name": self.index_name,
            "score": self.score,
            "components": {key: value.to_dict() for key, value in self.components.items()},
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
