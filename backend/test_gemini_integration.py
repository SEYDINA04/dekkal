#!/usr/bin/env python
"""
Dëkkal — Gemini LLM Integration Test Suite
Test script for Google Gemini API integration
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_gemini_connection():
    """Test Google Gemini API connectivity"""
    print("\n🧪 Test 1: Gemini API Connection")
    print("─" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not set in .env")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        response = model.generate_content("Say 'Dëkkal is ready!' in French")
        print(f"✅ Gemini response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_gemini_embedding():
    """Test Gemini Embedding API"""
    print("\n🧪 Test 2: Gemini Embedding Generation")
    print("─" * 50)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        text = "Zone basse avec sols argileux saturés et pluies extrêmes"
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="semantic_similarity"
        )
        
        embedding = result['embedding']
        print(f"✅ Embedding generated:")
        print(f"   - Dimension: {len(embedding)}")
        print(f"   - Sample values: {embedding[:5]}")
        print(f"   - Range: [{min(embedding):.4f}, {max(embedding):.4f}]")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_llm_service():
    """Test LLM Explainer Service"""
    print("\n🧪 Test 3: LLM Explainer Service")
    print("─" * 50)
    
    try:
        from api.services.llm_explainer import generate_explanation
        
        # Mock data
        features = {
            'elevation_m': 8.5,
            'slope_deg': 1.5,
            'p99_mm_day': 48,
            'p95_mm_day': 25,
            'clay_pct': 28,
            'soil_moisture_current': 0.16,
            'sar_delta_km2': 0.55,
            'drain_risk_score': 72,
            'zone_name': 'Pikine_Nord'
        }
        
        factors = [
            {"factor": "Low elevation (8.5m)", "impact": "High"},
            {"factor": "Saturated soil (0.16 m³/m³)", "impact": "High"},
            {"factor": "Extreme rainfall scenario (48mm/day)", "impact": "High"}
        ]
        
        result = generate_explanation(
            address="Pikine Technopole, Dakar",
            lat=14.75,
            lon=-17.39,
            score=62,
            risk_level="High",
            features=features,
            factors=factors,
            use_embeddings=True
        )
        
        print(f"✅ Explanation generated:")
        print(f"   - Provider: {result['provider']}")
        print(f"   - Status: {result['status']}")
        print(f"   - Narrative length: {len(result['narrative'])} chars")
        print(f"   - Embedding: {len(result['embedding']) if result['embedding'] else 0} dimensions")
        print(f"\n📝 Narrative (first 200 chars):\n{result['narrative'][:200]}...")
        return result['status'] == 'success'
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_explanations():
    """Test Batch Explanations"""
    print("\n🧪 Test 4: Batch Explanations")
    print("─" * 50)
    
    try:
        from api.services.llm_explainer import generate_batch_explanations
        
        # Mock batch data
        scores = [
            {
                "location": {
                    "lat": 14.75,
                    "lon": -17.39,
                    "address_normalized": "Pikine, Dakar"
                },
                "score": 62,
                "risk_level": "High",
                "explanations": [{"factor": "Low elevation", "impact": "High"}],
                "features": {"elevation_m": 8.5, "p99_mm_day": 48}
            },
            {
                "location": {
                    "lat": 14.72,
                    "lon": -17.50,
                    "address_normalized": "Almadies, Dakar"
                },
                "score": 25,
                "risk_level": "Low",
                "explanations": [{"factor": "High elevation", "impact": "Low"}],
                "features": {"elevation_m": 35.2, "p99_mm_day": 34}
            }
        ]
        
        results = generate_batch_explanations(scores, use_embeddings=False)
        
        print(f"✅ Batch processed:")
        print(f"   - Scores processed: {len(results)}")
        for i, r in enumerate(results, 1):
            status = r['llm_explanation']['status']
            print(f"   - Score {i}: {r['location']['address_normalized']} → {status}")
        
        return len(results) == len(scores)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_fastapi_endpoint():
    """Test FastAPI endpoint"""
    print("\n🧪 Test 5: FastAPI Endpoint")
    print("─" * 50)
    
    try:
        import requests
        
        # Make sure the server is running
        # Run with: python -m uvicorn main:app --reload --port 8000
        
        url = "http://localhost:8000/api/v1/score"
        payload = {
            "address": "Pikine Technopole, Dakar",
            "include_llm_explanation": True
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response:")
            print(f"   - Score: {data['score']}/100")
            print(f"   - Risk Level: {data['risk_level']}")
            print(f"   - LLM Explanation: {data.get('llm_explanation', {}).get('status', 'N/A')}")
            print(f"   - Processing time: {data['meta']['processing_time_ms']}ms")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI server not running on http://localhost:8000")
        print("   Start it with: python -m uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_semantic_similarity():
    """Test Semantic Similarity Search"""
    print("\n🧪 Test 6: Semantic Similarity")
    print("─" * 50)
    
    try:
        from api.services.llm_explainer import similarity_search, _get_gemini_embedding
        
        # Create mock embedding database
        scenarios = [
            {
                "id": "s1",
                "description": "Zone basse avec sols argileux et drainage faible",
                "zone": "Pikine",
                "score": 72
            },
            {
                "id": "s2",
                "description": "Plateau élevé avec bon drainage",
                "zone": "Almadies",
                "score": 15
            }
        ]
        
        # Add embeddings
        for scenario in scenarios:
            scenario['embedding'] = _get_gemini_embedding(scenario['description'])
        
        # Search
        query = "Zone inondable avec sols imperméables et pluies extrêmes"
        results = similarity_search(query, scenarios, top_k=1)
        
        if results:
            print(f"✅ Similarity search completed:")
            print(f"   - Query: '{query[:50]}...'")
            print(f"   - Top result: {results[0]['item']['zone']}")
            print(f"   - Similarity score: {results[0]['similarity_score']:.3f}")
            return True
        else:
            print(f"❌ No results found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("  🧪 Dëkkal — Gemini Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Gemini Connection", test_gemini_connection),
        ("Gemini Embedding", test_gemini_embedding),
        ("LLM Service", test_llm_service),
        ("Batch Explanations", test_batch_explanations),
        ("FastAPI Endpoint", test_fastapi_endpoint),
        ("Semantic Similarity", test_semantic_similarity),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("  📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} — {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
