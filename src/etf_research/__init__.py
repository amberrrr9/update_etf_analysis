"""ETF/index research domain modules.

This package is intentionally independent from the legacy stock decision
pipeline. ETF research should use deterministic scoring first and reserve LLMs
for explanation only.
"""

from src.etf_research.schemas import IndustryClue
from src.etf_research.signals import discover_industry_clue

__all__ = ["IndustryClue", "discover_industry_clue"]
