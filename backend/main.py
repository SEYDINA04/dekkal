"""
Dëkkal — FastAPI Application v2.0
XGBoost + Gemini LLM Explainer
"""
from dotenv import load_dotenv
load_dotenv()  # charge .env avant tout import de service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.score import router as score_router
from api.routers.batch_llm import router as batch_llm_router

app = FastAPI(
    title="Dëkkal Flood Risk API",
    description="Address-level flood risk scoring + Gemini LLM explanations for IARD insurers in Dakar, Senegal",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(score_router)
app.include_router(batch_llm_router)

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
