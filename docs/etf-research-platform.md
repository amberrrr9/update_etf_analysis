# AI ETF Research Platform

This document records the first-stage migration plan from a stock-centered AI
analysis system to an index-centered ETF research assistant.

## Product Principles

- Explain rather than predict.
- Analyze indices before ETFs whenever multiple ETFs track the same index.
- Use deterministic rules for evidence and clue discovery.
- Use LLMs only for interpretation and summarization.
- Do not produce buy/sell, target price, stop-loss, take-profit or position advice.

## MVP Architecture

```text
Market data
-> underlying index
-> deterministic industry clue discovery
-> industry / theme knowledge
-> LLM explanation
-> mapped ETFs
-> research report
```

The initial implementation introduces `src/etf_research/` as a separate domain
package. It does not modify the existing stock decision pipeline.

## New Domain Package

```text
src/etf_research/
  schemas.py
  scoring.py
  taxonomy.py
  knowledge_base.py
  etf_mapping.py
```

`signals.py` is the core of the MVP. It discovers transparent industry research
clues from index OHLCV data and optional benchmark/breadth data. It does not
produce a score, rating, rank or trading signal.

## Clue Discovery Rules

The first version records triggered evidence conditions:

- Daily return exceeds a transparent absolute threshold.
- Weekly return exceeds a transparent absolute threshold.
- Weekly relative strength versus a broad benchmark is notable.
- Turnover/amount is elevated versus the recent 20-day average.
- Constituent breadth is available and broad enough.

Unavailable optional inputs are marked in `data_quality` and excluded from the
research explanation instead of being silently treated as negative evidence.

## Next Steps

1. Add local seed files for ETF, index and index-to-ETF mappings.
2. Add a CLI smoke path for generating one index research result.
3. Add a research-only LLM prompt that forbids trading recommendations.
4. Add API endpoints under `/api/v1/etf-research`.
5. Add a Web research dashboard after backend payloads stabilize.
