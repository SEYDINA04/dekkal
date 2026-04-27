"""
Dëkkal — FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.score import router

app = FastAPI(
    title="Dëkkal Flood Risk API",
    description="Address-level flood risk scoring for IARD insurers in Dakar, Senegal",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "service": "Dëkkal Flood Risk API",
        "version": "1.0.0",
        "docs"   : "/docs",
        "health" : "/api/v1/health"
    }
