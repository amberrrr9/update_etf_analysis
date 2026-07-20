# AI ETF Research Platform

This document records the first-stage migration plan from a stock-centered AI
analysis system to an index-centered ETF research assistant.

## Product Principles

- Explain rather than predict.
- Analyze indices before ETFs whenever multiple ETFs track the same index.
- Use deterministic quantitative models for scoring.
- Use LLMs only for interpretation and summarization.
- Do not produce buy/sell, target price, stop-loss, take-profit or position advice.

## MVP Architecture

```text
Market data
-> underlying index
-> deterministic index health score
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

`scoring.py` is the core of the MVP. It calculates a deterministic
`IndexHealthScore` from index OHLCV data and optional benchmark/breadth data.

## Scoring Model

The first version uses seven rule-based components:

| Component | Weight |
| --- | ---: |
| Trend | 25 |
| Momentum | 20 |
| Relative strength | 20 |
| Volume | 10 |
| Volatility | 10 |
| Drawdown | 10 |
| Breadth | 5 |

Unavailable optional inputs are marked in `data_quality` and excluded from the
denominator instead of being silently treated as bearish signals.

## Next Steps

1. Add local seed files for ETF, index and index-to-ETF mappings.
2. Add a CLI smoke path for generating one index research result.
3. Add a research-only LLM prompt that forbids trading recommendations.
4. Add API endpoints under `/api/v1/etf-research`.
5. Add a Web research dashboard after backend payloads stabilize.
