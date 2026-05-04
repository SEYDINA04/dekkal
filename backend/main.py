"""
Dëkkal — FastAPI Application v2.0
XGBoost + Gemini LLM Explainer
"""
from dotenv import load_dotenv
load_dotenv()  # charge .env avant tout import de service

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers.score import router as score_router
from api.routers.batch_llm import router as batch_llm_router

app = FastAPI(
    title="Dëkkal Flood Risk API",
    description="Address-level flood risk scoring + Gemini LLM explanations for IARD insurers in Dakar, Senegal",
    version="2.0.0",
)

import os

_default_origins = "https://dekkal-public.vercel.app"
_raw = os.getenv("ALLOWED_ORIGINS", _default_origins)
allowed_origins = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(score_router)
app.include_router(batch_llm_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
        headers={"Access-Control-Allow-Origin": ", ".join(allowed_origins)},
    )

@app.get("/")
async def root():
    return {
        "service": "Dëkkal Flood Risk API",
        "version": "2.0.0",
        "models": {
            "scoring": "XGBoost v3.1 (Recall 95.8%)",
            "explanations": "Google Gemini 1.5 Pro"
        },
        "docs": "/docs",
        "health": "/api/v1/health",
        "llm_endpoints": [
            "/api/v1/score?include_llm_explanation=true",
            "/api/v1/batch-explain",
            "/api/v1/semantic-search",
            "/api/v1/vectorize-scenarios",
            "/api/v1/llm-status"
        ]
    }
