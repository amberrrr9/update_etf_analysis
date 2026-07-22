# -*- coding: utf-8 -*-
"""ETF research endpoints."""

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from src.etf_research.market_overview import build_market_overview

router = APIRouter()


@router.get("/market-overview")
async def get_market_overview() -> dict:
    """Return the full-market ETF research overview."""

    try:
        overview = await run_in_threadpool(build_market_overview)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - external data source should not leak stack traces.
        raise HTTPException(status_code=502, detail=f"AkShare market overview failed: {exc}") from exc
    return overview.to_dict()
