"""ETF/index research domain modules.

This package is intentionally independent from the legacy stock decision
pipeline. ETF research should use deterministic scoring first and reserve LLMs
for explanation only.
"""

from src.etf_research.scoring import calculate_index_health_score
from src.etf_research.schemas import IndexHealthScore

__all__ = ["IndexHealthScore", "calculate_index_health_score"]
