"""
Dëkkal — Batch & Semantic Search Router v1.0
Batch explanations + semantic similarity search using Gemini embeddings
Author: Babacar Ndao
"""
from fastapi import APIRouter, UploadFile, File, Query
from typing import List, Optional
import json
import tempfile
import os

from api.services.llm_explainer import (
    generate_batch_explanations,
    similarity_search,
    vectorize_scenario_library
)

router = APIRouter(prefix="/api/v1", tags=["batch-llm"])


@router.post("/batch-explain")
async def batch_explain(
    scores_file: UploadFile = File(..., description="JSON file with array of score responses"),
    use_embeddings: bool = Query(False, description="Generate Gemini embeddings for each score"),
    lang: str = Query("auto", description="Language for explanations: 'fr', 'en', or 'auto' (per-score field or address detection)")
):
    """
    Generate LLM explanations for multiple flood risk scores.
    Input: JSON array of score response objects.
    Output: Same scores with added 'llm_explanation' fields.
    'lang' overrides per-score lang field when set to 'fr' or 'en'.
    """
    try:
        contents = await scores_file.read()
        scores = json.loads(contents)

        if not isinstance(scores, list):
            scores = [scores]

        # Apply lang override to each score if explicitly set
        if lang in ("fr", "en"):
            for s in scores:
                s['lang'] = lang
        # else: each score keeps its own 'lang' field (or defaults to 'fr' in service)

        results = generate_batch_explanations(
            scores=scores,
            use_embeddings=use_embeddings
        )

        return {
            "status": "success",
            "count" : len(results),
            "lang_used": lang,
            "results": results
        }

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON file"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/semantic-search")
async def semantic_search_endpoint(
    query: str = Query(..., description="Flood scenario description (e.g., 'area with low elevation + high rainfall')"),
    embedding_db_file: Optional[str] = Query(None, description="Path to embedding database JSON file"),
    top_k: int = Query(3, ge=1, le=10, description="Number of similar results to return")
):
    """
    Find similar flood risk scores using semantic embeddings
    Great for finding analogous situations or historical patterns
    """
    try:
        if not embedding_db_file or not os.path.exists(embedding_db_file):
            return {
                "status": "error",
                "message": "Embedding database file not found. Please provide valid path."
            }
        
        # Load embedding database
        with open(embedding_db_file, 'r', encoding='utf-8') as f:
            embedding_db = json.load(f)
        
        # Search
        results = similarity_search(query, embedding_db, top_k)
        
        return {
            "status": "success",
            "query": query,
            "results_count": len(results),
            "results": [
                {
                    "similarity_score": r['similarity_score'],
                    "location": r['item'].get('location', {}),
                    "score": r['item'].get('score'),
                    "risk_level": r['item'].get('risk_level'),
                    "narrative": r['item'].get('llm_explanation', {}).get('narrative', '')[:200]
                }
                for r in results
            ]
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/vectorize-scenarios")
async def vectorize_scenarios(
    scenarios_file: UploadFile = File(..., description="JSON file with flood scenarios")
):
    """
    Pre-compute embeddings for a library of flood scenarios
    Enables fast semantic search during scoring
    """
    try:
        # Write temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            contents = await scenarios_file.read()
            tmp.write(contents.decode('utf-8'))
            tmp_path = tmp.name
        
        # Output path
        output_path = tmp_path.replace('.json', '_vectorized.json')
        
        # Vectorize
        vectorize_scenario_library(tmp_path, output_path)
        
        # Read result
        with open(output_path, 'r', encoding='utf-8') as f:
            vectorized = json.load(f)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "scenarios_vectorized": len(vectorized),
            "output_file": output_path,
            "sample": vectorized[0] if vectorized else None
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/llm-status")
async def llm_status():
    """Check LLM service availability and configuration"""
    import os
    from api.services.llm_explainer import LLM_PROVIDER
    
    return {
        "llm_provider": LLM_PROVIDER,
        "gemini_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "ollama_configured": True,  # Can always try
        "gemini_models": {
            "llm": "gemini-1.5-pro",
            "embeddings": "models/embedding-001"
        }
    }
