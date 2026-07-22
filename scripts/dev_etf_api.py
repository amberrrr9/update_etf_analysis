"""Lightweight ETF research API for local frontend development.

This avoids importing the legacy stock-analysis application while the ETF
research MVP is still being separated into its own backend surface.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from src.etf_research.market_overview import build_market_overview


app = FastAPI(title="ETF Research Dev API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/etf-research/market-overview")
async def get_market_overview() -> dict:
    try:
        overview = await run_in_threadpool(build_market_overview)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AkShare market overview failed: {exc}") from exc
    return overview.to_dict()
